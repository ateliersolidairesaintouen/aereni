from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


@dataclass
class Station:
    # aereni_id uniquely identify a station
    aereni_id: str

    # esp_id depends on the current esp installed in the station, it can vary if we replace the esp after a failure
    esp_id: str

    # a node_id uniquely identify a location where we installed a station
    node_id: str = None
    user: str = None  # identify the owner of the node (!= owner of the Station)
    address: str = None
    floor: int = None
    lat: Decimal = None
    lon: Decimal = None
    indoor: bool = False

    # if true, the data-points emitted by the station are considered real
    production: bool = False

    # identify the owner of the station (e.g atso, ben...)
    owner: str = None


@dataclass
class DataPoint:
    esp_id: str
    software_version: str = None
    pm25: Decimal = None
    pm10: Decimal = None
    temperature: Decimal = None
    pressure: Decimal = None
    humidity: Decimal = None
    # "samples" is the count of loops the main() function was running
    samples: int = None
    # "min_micro" and "max_micro" are the minimum and maximum running time of main() function
    min_micro: int = None
    max_micro: int = None
    # "signal" is the wifi strength
    signal: int = None


def parse_esp_json(json: Dict) -> DataPoint:
    """map a json, as sent by the esp, into a proper python object"""
    p = DataPoint(esp_id=json['esp8266id'],
                  software_version=json['software_version'])

    for data_value in json['sensordatavalues']:
        if data_value['value_type'] == 'SDS_P1':
            p.pm10 = Decimal(data_value['value'])
        elif data_value['value_type'] == 'SDS_P2':
            p.pm25 = Decimal(data_value['value'])
        elif data_value['value_type'] in ('BME280_temperature', 'BMP_temperature', 'temperature'):
            p.temperature = Decimal(data_value['value'])
        elif data_value['value_type'] in ('BME280_pressure', 'BMP_pressure'):
            p.pressure = Decimal(data_value['value'])
        elif data_value['value_type'] in ('BME280_humidity', 'humidity'):
            p.humidity = Decimal(data_value['value'])
        elif data_value['value_type'] == 'samples':
            p.samples = int(data_value['value'])
        elif data_value['value_type'] == 'min_micro':
            p.min_micro = int(data_value['value'])
        elif data_value['value_type'] == 'max_micro':
            p.max_micro = int(data_value['value'])
        elif data_value['value_type'] == 'signal':
            p.signal = int(data_value['value'])

    return p
