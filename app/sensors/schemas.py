from pydantic import BaseModel
from typing import Optional

class Sensor(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    joined_at: str
    last_seen: str
    type: str
    mac_address: str
    battery_level: float
    temperature: float
    humidity: float
    velocity: float
    description: str
    
    
    class Config:
        orm_mode = True
        
class SensorCreate(BaseModel):
    name: str
    longitude: float
    latitude: float
    type: str
    mac_address: str
    manufacturer: str
    model: str
    serie_number: str
    firmware_version: str
    description: str

class SensorData(BaseModel):
    velocity: Optional[float]
    temperature: Optional[float]
    humidity: Optional[float]
    battery_level: float
    last_seen: str
    
class SensorMongoProjection(BaseModel):
    id: int
    name: str
    location: dict
    type: str
    mac_address: str
    description: str
    serie_number: str
    firmware_version: str
    model: str
    manufacturer: str