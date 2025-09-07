# JWT Authentication Integration Guide

## Overview
This document describes the JWT authentication flow implemented in the B2A2 Car Auction Backend. The system uses:
- Access tokens (short-lived, 15 minutes) for API authentication
- Refresh tokens (1 day) stored in HTTP-only cookies
- Token rotation and blacklisting for security
- CSRF protection via SameSite cookie policy

## Endpoints

### 1. Login
**Endpoint**: `POST /api/users/jwt/token/`

**Request**:
```javascript
fetch('/api/users/jwt/token/', {
  method: 'POST',
  credentials: 'include',  // Required for cookies
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiL...",  // JWT access token
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "username": "username"
  }
}
```
Note: Refresh token is automatically set in HTTP-only cookie

### 2. Using Protected Endpoints
Add the access token to all API requests:

```javascript
fetch('/api/some-endpoint/', {
  method: 'GET',  // or POST, PUT, DELETE
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  credentials: 'include'  // Required for refresh token cookie
});
```

### 3. Token Refresh
Call this when access token expires (401 response).

**Endpoint**: `POST /api/users/jwt/refresh/`

```javascript
fetch('/api/users/jwt/refresh/', {
  method: 'POST',
  credentials: 'include'  // Required for cookies
});
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiL..."  // New access token
}
```

### 4. Logout
**Endpoint**: `POST /api/users/logout/`

```javascript
fetch('/api/users/logout/', {
  method: 'POST',
  credentials: 'include'  // Required for cookies
});
```

## Implementation Example

```javascript
// auth.js - Authentication service
class AuthService {
  constructor() {
    this.accessToken = null;
    this.refreshPromise = null;
  }

  async login(email, password) {
    const response = await fetch('/api/users/jwt/token/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.accessToken = data.access;
    return data.user;
  }

  async refreshToken() {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = fetch('/api/users/jwt/refresh/', {
      method: 'POST',
      credentials: 'include'
    })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error('Refresh failed');
      }
      const data = await response.json();
      this.accessToken = data.access;
      return this.accessToken;
    })
    .finally(() => {
      this.refreshPromise = null;
    });

    return this.refreshPromise;
  }

  async logout() {
    await fetch('/api/users/logout/', {
      method: 'POST',
      credentials: 'include'
    });
    this.accessToken = null;
  }

  // Wrapper for API calls that handles token refresh
  async fetchWithAuth(url, options = {}) {
    const requestOptions = {
      ...options,
      credentials: 'include',
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    };

    try {
      const response = await fetch(url, requestOptions);
      
      if (response.status === 401) {
        // Token expired, try to refresh
        await this.refreshToken();
        
        // Retry original request with new token
        requestOptions.headers['Authorization'] = `Bearer ${this.accessToken}`;
        return fetch(url, requestOptions);
      }
      
      return response;
    } catch (error) {
      if (error.message === 'Refresh failed') {
        // Refresh token expired or invalid
        // Redirect to login
        window.location.href = '/login';
      }
      throw error;
    }
  }
}

// Usage example:
const auth = new AuthService();

// Login
try {
  const user = await auth.login('user@example.com', 'password');
  console.log('Logged in as:', user);
} catch (error) {
  console.error('Login failed:', error);
}

// API calls
try {
  const response = await auth.fetchWithAuth('/api/some-endpoint/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ some: 'data' })
  });
  const data = await response.json();
} catch (error) {
  console.error('API call failed:', error);
}

// Logout
await auth.logout();
```

## Security Considerations

1. **Token Storage**:
   - Store access token in memory only (not localStorage/sessionStorage)
   - Refresh token is automatically handled via HTTP-only cookie

2. **CSRF Protection**:
   - SameSite cookie policy helps prevent CSRF attacks
   - Consider adding CSRF token for extra protection in browser environments

3. **Error Handling**:
   - Implement proper error handling for network issues
   - Handle token refresh failures appropriately

4. **Concurrent Requests**:
   - Use token refresh promise to prevent multiple simultaneous refresh attempts
   - Queue requests during refresh

5. **Logout**:
   - Clear all auth state on logout
   - Consider implementing server-side token revocation for sensitive applications

## Production Considerations

1. **HTTPS**:
   - Always use HTTPS in production
   - Secure cookie flag is enabled for refresh tokens

2. **Domain Configuration**:
   - Configure cookie domain for your production domain
   - Update CORS settings accordingly

3. **Error Recovery**:
   - Implement retry logic for network errors
   - Have a fallback for failed token refreshes
