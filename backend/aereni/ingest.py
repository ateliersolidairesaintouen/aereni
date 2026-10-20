from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError

from aereni.databases import postgresql, Measurement, Station
from aereni.inventory import get_station_by_esp_id

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


# Particle sensors supported by the airRohr firmware, as named in its
# "sensordatavalues": SDS011 (SDS_), Plantower PMS1003 to PMS7003 (PMS_).
# P1 is PM10 and P2 is PM2.5 for every sensor.
PM10_VALUE_TYPES = ('SDS_P1', 'PMS_P1')
PM25_VALUE_TYPES = ('SDS_P2', 'PMS_P2')


def to_decimal(value) -> Optional[Decimal]:
    """Convertit une valeur envoyée par l'ESP ; None si elle est invalide ou non finie (nan, inf)."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return d if d.is_finite() else None


def to_int(value) -> Optional[int]:
    d = to_decimal(value)
    return int(d) if d is not None else None


def flag_to_int(value) -> Optional[int]:
    """production / indoor peuvent être un booléen ou une chaîne de bits ('0' / '1')
    selon le schéma de la base : on les ramène toujours à 0 ou 1."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return 1 if int(value, 2) else 0
        except ValueError:
            return 1 if value.strip().lower() in ('true', 't', 'yes') else 0
    return 1 if value else 0


def parse_esp_json(payload: Dict) -> DataPoint:
    """map a json, as sent by the esp, into a proper python object"""
    p = DataPoint(
        esp_id=str(payload['esp8266id']),
        software_version=payload.get('software_version')
    )

    for data_value in payload.get('sensordatavalues', []):
        value_type = data_value.get('value_type')
        value = data_value.get('value')

        if value_type in PM10_VALUE_TYPES:
            p.pm10 = to_decimal(value)
        elif value_type in PM25_VALUE_TYPES:
            p.pm25 = to_decimal(value)
        elif value_type in ('BME280_temperature', 'BMP_temperature', 'temperature'):
            p.temperature = to_decimal(value)
        elif value_type in ('BME280_pressure', 'BMP_pressure'):
            p.pressure = to_decimal(value)
        elif value_type in ('BME280_humidity', 'humidity'):
            p.humidity = to_decimal(value)
        elif value_type == 'samples':
            p.samples = to_int(value)
        elif value_type == 'min_micro':
            p.min_micro = to_int(value)
        elif value_type == 'max_micro':
            p.max_micro = to_int(value)
        elif value_type == 'signal':
            p.signal = to_int(value)

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
        production=flag_to_int(s.production) or 0,
        indoor=flag_to_int(s.indoor),
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
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    try:
        data_point = parse_esp_json(request.get_json())
    except (KeyError, TypeError, AttributeError):
        return jsonify({"error": 400, "message": "Malformed payload"}), 400

    try:
        station = get_station_by_esp_id(data_point.esp_id)
        if station is None:
            # On ne journalise que l'esp_id, pas le contenu complet de la requête
            current_app.logger.warning(
                "dropping a data point because esp_id=%s is not known in the inventory",
                data_point.esp_id
            )
            return jsonify({"error": 400, "message": f"There is no station with esp_id={data_point.esp_id}"}), 400

        try:
            write_to_postgresql(data_point, station)
        except SQLAlchemyError:
            # Sans rollback, la session reste invalide et les requêtes suivantes échouent
            postgresql.session.rollback()
            current_app.logger.exception("could not store a measurement for esp_id=%s", data_point.esp_id)
            return jsonify({"error": 500, "message": "Could not store the measurement"}), 500

        return jsonify({"status": "success"})

    except Exception:
        current_app.logger.exception("!!!!!! INGEST ERROR !!!!!! please fix !!!! <3")
        raise
