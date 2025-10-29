from drf_yasg import openapi
from rest_framework import serializers
from django.db.utils import OperationalError, ProgrammingError
from django.apps import apps

FIELD_TYPE_MAP = {
    serializers.CharField: openapi.TYPE_STRING,
    serializers.EmailField: openapi.TYPE_STRING,
    serializers.IntegerField: openapi.TYPE_INTEGER,
    serializers.DecimalField: openapi.TYPE_NUMBER,
    serializers.FloatField: openapi.TYPE_NUMBER,
    serializers.BooleanField: openapi.TYPE_BOOLEAN,
    serializers.DateField: openapi.TYPE_STRING,
    serializers.DateTimeField: openapi.TYPE_STRING,
    serializers.ImageField: openapi.TYPE_FILE,
    serializers.FileField: openapi.TYPE_FILE,
    serializers.ListField: openapi.TYPE_ARRAY,
}

MAX_ENUM_CHOICES = 50  # safety limit to avoid huge specs

def _coerce_enum(values):
    coerced = []
    for v in values:
        try:
            coerced.append(str(v))
        except Exception:
            # fallback placeholder
            coerced.append("<unserializable>")
    return coerced

def _field_type(field):
    for k, v in FIELD_TYPE_MAP.items():
        if isinstance(field, k):
            return v
    return openapi.TYPE_STRING

def _build_description(field, name):
    parts = []
    if getattr(field, 'help_text', None):
        parts.append(str(field.help_text))
    if getattr(field, 'required', False):
        parts.append('(required)')
    if hasattr(field, 'max_length') and field.max_length:
        parts.append(f'max_length={field.max_length}')
    return ' '.join(parts) or f'{name} field'

def _attempt_enum(field):
    if not hasattr(field, 'choices'):
        return None
    try:
        if field.choices:
            raw_choices = list(field.choices.keys()) if isinstance(field.choices, dict) else list(field.choices)
            if len(raw_choices) <= MAX_ENUM_CHOICES:
                return _coerce_enum(raw_choices)
    except (OperationalError, ProgrammingError):
        return None
    return None

def _param_for_field(name, field, location):
    field_type = _field_type(field)
    description = _build_description(field, name)
    # Guard relational/queryset fields pre-migrate
    if hasattr(field, 'queryset') and field.queryset is not None:
        try:
            field.queryset.model
        except (OperationalError, ProgrammingError):
            return openapi.Parameter(name, location, description=description, required=field.required, type=field_type)
    enum = _attempt_enum(field)
    # Handle ListField (TYPE_ARRAY) needing items attribute
    items = None
    if field_type == openapi.TYPE_ARRAY:
        child_type = openapi.TYPE_STRING
        if hasattr(field, 'child') and field.child is not None:
            try:
                child_type = _field_type(field.child)
            except Exception:
                child_type = openapi.TYPE_STRING
        # Swagger 2.0 does not support array of files directly; downgrade to single file param hint.
        if child_type == openapi.TYPE_FILE:
            description = description + ' (upload one or more files by selecting multiple; repeat key if needed)'
            field_type = openapi.TYPE_FILE
            items = None
        else:
            items = openapi.Items(type=child_type)
    return openapi.Parameter(
        name,
        location,
        description=description,
        required=field.required,
        type=openapi.TYPE_STRING if enum else field_type,
        enum=enum,
        items=items
    )

def generate_form_parameters(serializer_cls, location=openapi.IN_FORM):
    # If apps not ready (during migrations), avoid instantiating serializer to prevent DB hits.
    if not apps.ready:
        return []
    try:
        serializer = serializer_cls()
    except (OperationalError, ProgrammingError):
        return []
    params = []
    for name, field in serializer.fields.items():
        if getattr(field, 'read_only', False):
            continue
        params.append(_param_for_field(name, field, location))
    return params

def safe_generate_form_parameters(serializer_cls, location=openapi.IN_FORM):
    """Wrapper that never raises due to DB initialization state.
    Returns empty list if any OperationalError/ProgrammingError occurs.
    """
    try:
        return generate_form_parameters(serializer_cls, location)
    except (OperationalError, ProgrammingError):
        return []
