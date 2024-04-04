from flask import Blueprint, request, jsonify, abort
import json

from aereni.inventory import get_station_by_esp_id, get_station_by_id, Station
from aereni.databases import influx

stats_blueprint = Blueprint('stats', __name__)


def last_average(duration="10m", production=True):
    query_api = influx.query_api()

    results = query_api.query(f'from(bucket: "aereni") |> range(start: -{duration}) |> filter(fn: (r) => r["_measurement"] == "{"production" if production else "test"}") |> filter(fn: (r) => r["_field"] == "humidity" or r["_field"] == "pm10" or r["_field"] == "pm25" or r["_field"] == "pressure" or r["_field"] == "temperature") |> mean() |> pivot(rowKey: ["_start"], columnKey: ["_field"], valueColumn: "_value") |> yield()').to_values(columns=["pm25", "pm10", "humidity", "temperature", "pressure"])


    for r in results:
        return {
            'pm25': round(r[0], 2),
            'pm10': round(r[1], 2),
            'humidity': round(r[2], 2),
            'temperature': round(r[3], 2),
            'pressure': round(r[4], 2)
        }


    return {
        'pm25': 0,
        'pm10': 0,
        'humidity': 0,
        'temperature': 0,
        'pressure': 0
    }


def pm_color(value):
    color = None
    if value < 51:
        color = 'rgba( 0, 153, 102,.95)'  # Vert 0-50
    elif value < 101:
        color = 'rgba( 255, 222, 51,.95)'  # Jaune 51-100
    elif value < 151:
        color = 'rgba( 255, 153, 51,.95)'  # Orange 101-150
    elif value < 201:
        color = 'rgba( 204, 0, 51,.95)'  # Rouge 151-200
    elif value < 301:
        color = 'rgba( 102, 0, 153,.95)'  # Violet 201-300
    elif value > 301:
        color = 'rgba( 126, 0, 35,.95)'  # Marron 301+
    return color


@stats_blueprint.get("/stats/average")
def api_average():
    production = request.args.get('production', True, type=lambda v: v.lower() == 'true')
    measures = last_average(production=production)
    return jsonify({
        'measures': measures,
        'colors': {
            'pm25': pm_color(measures['pm25']),
            'pm10': pm_color(measures['pm10'])
        }
    })

@stats_blueprint.get("/stats/last_measurement")
def api_last_measurement():
    query_api = influx.query_api()
    results = query_api.query('from(bucket: "aereni") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "test") |> filter(fn: (r) => r["_field"] == "humidity" or r["_field"] == "pm10" or r["_field"] == "pm25" or r["_field"] == "pressure" or r["_field"] == "temperature") |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value") |> yield()').to_values(columns=["pm25", "pm10", "humidity", "temperature", "pressure", "esp_id", "_time"])


    stations_done = set()
    data = []

    for r in results:
        esp_id = r[5]
        print(r)
        if esp_id not in stations_done:
            stations_done.add(esp_id)
            station = get_station_by_esp_id(esp_id)
            data.append({
                'id': station.id,
                'esp_id': station.esp_id,
                'name': station.name,
                'lon': station.lon,
                'lat': station.lat,
                'pm25': r[0],
                'pm10': r[1],
                'humidity': r[2],
                'temperature': r[3],
                'pressure': r[4],
                'date': r[6]
            })

    return jsonify(data)

@stats_blueprint.get("/stats/history/<id>")
def api_history(id: str):
    station = get_station_by_id(id)
    if not station: abort(404)

    duration = request.args.get("duration", "10m", type=str)

    query_api = influx.query_api()

    results = query_api.query(f'from(bucket: "aereni") |> range(start: -{duration}) |> filter(fn: (r) => r["_measurement"] == "test") |> filter(fn: (r) => r["station_id"] == "{id}") |> filter(fn: (r) => r["_field"] == "humidity" or r["_field"] == "pm10" or r["_field"] == "pm25" or r["_field"] == "pressure" or r["_field"] == "temperature") |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value") |> yield()').to_values(columns=["pm25", "pm10", "humidity", "temperature", "pressure", "esp_id", "_time"])

    data = []
    for r in results:
        data.append({
            'pm25': r[0],
            'pm10': r[1],
            'humidity': r[2],
            'temperature': r[3],
            'pressure': r[4],
            'date': r[6]
        })

    return jsonify({
        'id': station.id,
        'esp_id': station.esp_id,
        'address': station.address,
        'name': station.name,
        'lon': station.lon,
        'lat': station.lat,
        'data': data
    })

@stats_blueprint.get("/stats/last_measurement_umap")
def api_last_measurement_umap():
    query_api = influx.query_api()
    results = query_api.query('from(bucket: "aereni") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "test") |> filter(fn: (r) => r["_field"] == "humidity" or r["_field"] == "pm10" or r["_field"] == "pm25" or r["_field"] == "pressure" or r["_field"] == "temperature") |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value") |> yield()').to_values(columns=["pm25", "pm10", "humidity", "temperature", "pressure", "esp_id", "_time"])


    stations_done = set()
    data = []

    for r in results:
        esp_id = r[5]
        print(r)
        if esp_id not in stations_done:
            stations_done.add(esp_id)
            station = get_station_by_esp_id(esp_id)


            pm25 = r[0] if r[0] else 0.0
            pm10 = r[1] if r[1] else 0.0
            humidity = r[2] if r[2] else 0.0
            temperature = r[3] if r[3] else 0.0
            pressure = r[4] if r[4] else 0.0

            lon = station.lon if station.lon else "1.00"
            lat = station.lat if station.lat else "1.00"


            data.append({
                "type": "Feature",
                "properties": {
                    "name": station.name,
                    "temp": temperature,
                    "hum": humidity,
                    "pm10": pm10,
                    "pm25": pm25,
                    "pressure": pressure,
                    "_umap_options": {
                        "color": "Red",
                        "popupTemplate": "Table",
                    }
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(lon),
                        float(lat)
                    ]

                }
            })

    return jsonify({
        "type": "FeatureCollection",
        "features": data
    })
