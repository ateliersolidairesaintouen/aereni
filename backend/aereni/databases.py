from influxdb_flask import InfluxDB
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

postgresql = SQLAlchemy()
influx = InfluxDB()

@dataclass
class Station(postgresql.Model):
    __tablename__ = 'station'

    # uniquely identify a station
    id: str = postgresql.Column(postgresql.String, primary_key=True)

    # name of the Station
    name: str = postgresql.Column(postgresql.String, unique=True, nullable=False)

    # esp_id depends on the current esp installed in the station, it can vary if we replace the esp after a failure
    esp_id: str = postgresql.Column(postgresql.String, unique=True, nullable=False)

    # sensebox_id as defined in opensensemap platform
    sensebox_id: str = postgresql.Column(postgresql.String, unique=True, nullable=True)

    # a node_id uniquely identify a location where we installed a station
    node_id: str = postgresql.Column(postgresql.String, unique=True, nullable=True)

    # identify the owner of the node (!= owner of the Station)
    user: str = postgresql.Column(postgresql.String, unique=False, nullable=True)
    address: str = postgresql.Column(postgresql.String, unique=False, nullable=True)
    floor: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    lat: float = postgresql.Column(postgresql.Numeric, unique=False, nullable=True)
    lon: float = postgresql.Column(postgresql.Numeric, unique=False, nullable=True)
    indoor: bool = postgresql.Column(postgresql.Boolean, unique=False, nullable=True)

    # if true, the data-points emitted by the station are considered real
    production: bool = postgresql.Column(postgresql.Boolean, unique=False, nullable=False, default=False)

    # identify the owner of the station (e.g atso, ben...)
    owner: str = postgresql.Column(postgresql.String, unique=False, nullable=False, default="ATSO")

    comment: str = postgresql.Column(postgresql.String, unique=False, nullable=True, default="")

    def __repr__(self):
        return '<Station %r>' % self.name



@dataclass
class Measurement(postgresql.Model):
    __tablename__ = 'measurement'

    id: int = postgresql.Column(postgresql.Integer, primary_key=True)
    pm25: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    pm10: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    humidity: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    temperature: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    pressure: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    datetime: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)

    esp_id: float = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    station_id: float = postgresql.Column(postgresql.Float, unique=False, nullable=True)
    production: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    indoor: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)

    # Monitoring
    software_version: str = postgresql.Column(postgresql.String, unique=False, nullable=True)
    samples: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    signal: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    min_micro: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    max_micro: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
