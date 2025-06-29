import requests
import random
import uuid
from datetime import datetime, timedelta

# --- CONFIG ---
API_BASE = "http://127.0.0.1:8000/api/auction/"
USERS_API = "http://127.0.0.1:8000/api/users/"

# You may want to update these tokens for your test users
USER_TOKENS = [
    'Token c6aa9fd8be7e54eb44eb0219907cf38eae5bf0d2',
    
]

# Helper to get all vehicles
vehicles = requests.get(f"{API_BASE}vehicles/").json()
print("Fetched vehicles:", vehicles)
vehicle_ids = [v['id'] for v in vehicles]

# Helper to get all existing auctions (to avoid duplicates)
existing_auctions = requests.get(f"{API_BASE}auctions/").json()
# Use vehicle_details['id'] for nested vehicle UUID
auction_vehicle_ids = set(
    a['vehicle_details']['id'] if 'vehicle_details' in a and a['vehicle_details'] else a.get('vehicle')
    for a in existing_auctions
)

# Helper to create auctions for each vehicle
auctions_created = []
auction_starting_prices = {}
for vehicle_id in vehicle_ids:
    print(f"Processing vehicle_id: {vehicle_id} (type: {type(vehicle_id)})")
    if not vehicle_id:
        print(f"Skipping invalid vehicle_id: {vehicle_id}")
        continue
    if vehicle_id in auction_vehicle_ids:
        print(f"Skipping vehicle {vehicle_id} (auction already exists)")
        continue
    auction_data = {
        "vehicle": vehicle_id,
        "starting_price": random.randint(5000, 20000),
        "start_time": (datetime.now() + timedelta(minutes=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=3)).isoformat(),
    }
    print(f"Auction data to POST: {auction_data}")
    headers = {"Authorization": USER_TOKENS[0]} if USER_TOKENS else {}
    resp = requests.post(f"{API_BASE}auctions/", json=auction_data, headers=headers)
    if resp.status_code == 201:
        print(f"Created auction for vehicle {vehicle_id}")
        auction_id = resp.json()['id']
        auctions_created.append(auction_id)
        auction_starting_prices[auction_id] = auction_data['starting_price']
    else:
        print(f"Failed to create auction for vehicle {vehicle_id}: {resp.status_code} {resp.text}")
        print(f"Response content: {resp.content}")

# Helper to place bids on each auction
for auction_id in auctions_created:
    starting_price = auction_starting_prices[auction_id]
    for i, token in enumerate(USER_TOKENS):
        bid_data = {
            "auction": auction_id,
            "bid_amount": random.randint(starting_price + 1000, starting_price + 5000)
        }
        headers = {"Authorization": token}
        resp = requests.post(f"{API_BASE}bids/", json=bid_data, headers=headers)
        if resp.status_code == 201:
            print(f"User {i+1} placed bid on auction {auction_id}")
        else:
            print(f"Failed to place bid for user {i+1} on auction {auction_id}: {resp.status_code} {resp.text}")

print("Auction and bid population complete.")
