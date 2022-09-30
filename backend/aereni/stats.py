from flask import Blueprint, request, jsonify

from aereni.databases import influx

stats_blueprint = Blueprint('stats', __name__)


def last_average(duration="10m", production=True):
    results = list(
        influx.query(
            f'SELECT mean(*) FROM {"production" if production else "test"} WHERE time > now() - {duration}').get_points()
    )

    if len(results) == 0:
        return {
            'pm25': 0,
            'pm10': 0,
            'humidity': 0,
            'temperature': 0,
            'pressure': 0
        }

    return {
        'pm25': round(results[0]['mean_pm25'], 2),
        'pm10': round(results[0]['mean_pm10'], 2),
        'humidity': round(results[0]['mean_humidity'], 2),
        'temperature': round(results[0]['mean_temperature'], 2),
        'pressure': round(results[0]['mean_pressure'], 2)
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

    exemple = """
    [
        {
            "id": "1",
            "name": "Mairie",
            "long": 48.911856,
            "lat": 2.333764,
            "pm25": 45,
            "pm10": 10,
            "temperature": 8,
            "pressure": 42,
            "humidity": 42,
            "date": "29/09/2022 21:45"
        },
        {
            "id": "2",
            "name": "Atelier",
            "long": 48.92,
            "lat": 2.333,
            "pm25": 20,
            "pm10": 10,
            "temperature": 8,
            "pressure": 42,
            "humidity": 42,
            "date": "29/09/2022 21:42"
        },
        {
            "id": "3",
            "name": "ID 3",
            "long": 48.902,
            "lat": 2.34,
            "pm25": 10,
            "pm10": 10,
            "temperature": 8,
            "pressure": 42,
            "humidity": 42,
            "date": "09/02/2022 21:45"
        },
        {
            "id": "4",
            "name": "ID 4",
            "long": 48.905,
            "lat": 2.32,
            "pm25": 80,
            "pm10": 10,
            "temperature": 8,
            "pressure": 42,
            "humidity": 42,
            "date": "09/02/2022 21:48"
        }
    ]"""

    return jsonify(exemple)
