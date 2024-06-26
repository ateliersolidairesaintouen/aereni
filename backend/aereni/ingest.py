import traceback
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from typing import Dict

from flask import Blueprint, jsonify, request
from influxdb_client.client.write_api import SYNCHRONOUS
from aereni.config import config
from aereni.databases import postgresql, Measurement, Station
from aereni.inventory import get_station_by_esp_id, Station

ingest_blueprint = Blueprint('ingest', __name__)

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
    p = DataPoint(esp_id=json['esp8266id'], software_version=json['software_version'])

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


def write_to_postgresql(p: DataPoint, s: Station):
    date = datetime.now().timestamp()
    item = Measurement(
        pm25=p.pm25,
        pm10=p.pm10,
        humidity=p.humidity,
        temperature=p.temperature,
        pressure=p.pressure,
        datetime=date,
        esp_id=s.esp_id,
        station_id=s.id,
        production=s.production,
        indoor=s.indoor,
        software_version=p.software_version,
        samples=p.samples,
        min_micro=p.min_micro,
        max_micro=p.max_micro,
        signal=p.signal
    )

    postgresql.session.add(item)
    postgresql.session.commit()

@ingest_blueprint.post("/ingest")
def api_ingest():
    try:
        if not request.is_json:
            return jsonify({"error": 400, "message": "Invalid request"}), 400

        data_point = parse_esp_json(request.json)
        station = get_station_by_esp_id(data_point.esp_id)
        if station is None:
            print("error: dropping a data point because the esp_id is not known in the inventory", request.data)
            return jsonify({"error": 400, "message": f"There is no station with esp_id={data_point.esp_id}"}), 400

        #write_to_influx(data_point, station)
        try:
            write_to_postgresql(data_point, station)
            return jsonify({"status": "success"})
        except SQLAlchemyError as e:
            return jsonify({"error": 400, "message": str(e)}), 400

    except Exception as e:
        print("!!!!!! INGEST ERROR !!!!!! please fix !!!! <3")
        print(traceback.format_exc())
        raise e
