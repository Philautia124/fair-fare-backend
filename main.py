from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from geopy.distance import geodesic

app = FastAPI(title="Fair Fare API")

class LocationPoint(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        orm_mode = True

class Trip(BaseModel):
    id: Optional[int]
    start_location: LocationPoint
    current_location: LocationPoint
    distance_km: float = 0
    fare_amount: float = 0
    is_active: bool = True

    class Config:
        orm_mode = True

# In-memory storage (replace with database in production)
trips: List[Trip] = []
current_trip_id = 0

@app.get("/")
async def root():
    return {"message": "Welcome to Fair Fare API"}

@app.post("/trips/start")
async def start_trip(location: LocationPoint):
    global current_trip_id
    current_trip_id += 1
    
    new_trip = Trip(
        id=current_trip_id,
        start_location=location,
        current_location=location
    )
    trips.append(new_trip)
    return new_trip

@app.post("/trips/{trip_id}/update")
async def update_trip(trip_id: int, new_location: LocationPoint):
    trip = next((t for t in trips if t.id == trip_id and t.is_active), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Active trip not found")
    
    # Calculate distance between current and new location
    prev_location = (trip.current_location.latitude, trip.current_location.longitude)
    new_loc = (new_location.latitude, new_location.longitude)
    distance = geodesic(prev_location, new_loc).kilometers
    
    # Update trip
    trip.current_location = new_location
    trip.distance_km += distance
    trip.fare_amount = calculate_fare(trip.distance_km)
    
    return trip

@app.post("/trips/{trip_id}/end")
async def end_trip(trip_id: int):
    trip = next((t for t in trips if t.id == trip_id and t.is_active), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Active trip not found")
    
    trip.is_active = False
    return trip

@app.get("/trips/{trip_id}")
async def get_trip(trip_id: int):
    trip = next((t for t in trips if t.id == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

def calculate_fare(distance_km: float) -> float:
    # Example fare calculation (customize according to your needs)
    base_fare = 40  # Base fare in PHP
    per_km_rate = 13.50  # Rate per kilometer in PHP
    return base_fare + (distance_km * per_km_rate) 