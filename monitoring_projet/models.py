from dataclasses import dataclass
from dal import UserDao


@dataclass
class Iot:
    mac:str

@dataclass
class TemperatureIot:
    mac:str
    temp:float
    datetime:str

@dataclass
class Pc:
    user_id:int
    adressIp:str
    memoryUsage:float
    processeurUsage:float
    usageDisque:float
    datetime: str

@dataclass
class User:
    username:str
    email:str
    password:str
    isAdmin:str

@dataclass
class Weather:
    id_city: int
    date: str
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float

@dataclass
class Ville:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    id:int
    name:str