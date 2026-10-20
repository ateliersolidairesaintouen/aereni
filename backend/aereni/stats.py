import datetime

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from aereni.inventory import get_station_by_id
from aereni.databases import postgresql, Station, Measurement

stats_blueprint = Blueprint('stats', __name__)

# Le CORS est géré par nginx (location /stats). Ne pas ajouter d'en-têtes
# Access-Control-* ici : ils seraient envoyés en double ("*, *") et le
# navigateur bloquerait la requête.

# Une mesure est considérée comme "récente" pendant cette durée (en secondes)
RECENT_WINDOW = 3600
# Fenêtre de calcul de la moyenne de /stats/average (10 minutes)
AVERAGE_WINDOW = 600
# Durée maximale acceptée par /stats/history (30 jours)
MAX_HISTORY_DURATION = 30 * 24 * 3600


def last_average(duration=AVERAGE_WINDOW, production=1):
    """Moyenne de toutes les mesures reçues dans les `duration` dernières secondes."""
    since = datetime.datetime.now().timestamp() - duration

    row = (
        postgresql.session.query(
            func.avg(Measurement.pm25),
            func.avg(Measurement.pm10),
            func.avg(Measurement.humidity),
            func.avg(Measurement.temperature),
            func.avg(Measurement.pressure),
        )
        .filter(Measurement.datetime > since)
        .filter(Measurement.production == production)
        .one()
    )

    keys = ('pm25', 'pm10', 'humidity', 'temperature', 'pressure')
    # Aucune mesure sur la période : 0, comme avant
    return {key: round(float(value), 2) if value is not None else 0 for key, value in zip(keys, row)}


def pm_color(value):
    if value is None:
        return None
    if value < 51:
        return 'rgba( 0, 153, 102,.95)'  # Vert 0-50
    if value < 101:
        return 'rgba( 255, 222, 51,.95)'  # Jaune 51-100
    if value < 151:
        return 'rgba( 255, 153, 51,.95)'  # Orange 101-150
    if value < 201:
        return 'rgba( 204, 0, 51,.95)'  # Rouge 151-200
    if value < 301:
        return 'rgba( 102, 0, 153,.95)'  # Violet 201-300
    return 'rgba( 126, 0, 35,.95)'  # Marron 301+


def parse_production(default=True):
    """Lit ?production=true|false et renvoie 1 ou 0 (valeur de Measurement.production)."""
    return int(request.args.get('production', default, type=lambda v: v.lower() == 'true'))


def to_float(value):
    """lon/lat sont des Numeric (Decimal) : jsonify les enverrait sous forme de chaînes."""
    return float(value) if value is not None else None


def latest_measurements(production=None):
    """Dernière mesure de chaque station sur la dernière heure.

    Renvoie une liste de tuples (station, mesure). Si `production` vaut 0 ou 1,
    seules les mesures correspondantes sont retenues.
    """
    since = datetime.datetime.now().timestamp() - RECENT_WINDOW

    query = (
        postgresql.session.query(Station, Measurement)
        .filter(Measurement.esp_id == Station.esp_id)
        .filter(Measurement.datetime > since)
    )
    if production is not None:
        query = query.filter(Measurement.production == production)

    # Tri décroissant : la première mesure rencontrée pour une station est la plus récente
    query = query.order_by(Measurement.datetime.desc())

    latest = {}
    for station, measure in query.all():
        if station.id not in latest:
            latest[station.id] = (station, measure)

    return list(latest.values())


@stats_blueprint.get("/stats/average")
def api_average():
    measures = last_average(production=parse_production())
    return jsonify({
        'measures': measures,
        'colors': {
            'pm25': pm_color(measures['pm25']),
            'pm10': pm_color(measures['pm10'])
        }
    })


@stats_blueprint.get("/stats/last_measurement")
def api_last_measurement():
    data = []

    for station, measure in latest_measurements(parse_production()):
        data.append({
            'id': station.id,
            'esp_id': station.esp_id,
            'name': station.name,
            'lon': to_float(station.lon),
            'lat': to_float(station.lat),
            'pm25': measure.pm25,
            'pm10': measure.pm10,
            'humidity': measure.humidity,
            'temperature': measure.temperature,
            'pressure': measure.pressure,
            'date': measure.datetime
        })

    return jsonify(data)


@stats_blueprint.get("/stats/history/<id>")
def api_history(id: str):
    station = get_station_by_id(id)
    if not station:
        abort(404)

    duration = request.args.get("duration", 3600 * 24, type=int)
    duration = min(max(duration, 1), MAX_HISTORY_DURATION)

    since = datetime.datetime.now().timestamp() - duration
    results = (
        postgresql.session.query(Measurement)
        .filter(Measurement.station_id == id)
        .filter(Measurement.datetime > since)
        .order_by(Measurement.datetime.desc())
        .all()
    )

    data = []
    for measure in results:
        data.append({
            'pm25': measure.pm25,
            'pm10': measure.pm10,
            'humidity': measure.humidity,
            'temperature': measure.temperature,
            'pressure': measure.pressure,
            'date': measure.datetime
        })

    # L'adresse (domicile d'un habitant) n'est volontairement plus exposée
    # sur cette route publique.
    return jsonify({
        'id': station.id,
        'esp_id': station.esp_id,
        'name': station.name,
        'lon': to_float(station.lon),
        'lat': to_float(station.lat),
        'data': data
    })


@stats_blueprint.get("/stats/last_measurement_umap")
def api_last_measurement_umap():
    features = []

    for station, measure in latest_measurements(parse_production()):
        # Sans coordonnées, la station ne peut pas être placée sur la carte
        if station.lon is None or station.lat is None:
            continue

        features.append({
            "type": "Feature",
            "properties": {
                "name": station.name,
                "temp": measure.temperature or 0.0,
                "hum": measure.humidity or 0.0,
                "pm10": measure.pm10 or 0.0,
                "pm25": measure.pm25 or 0.0,
                "pressure": measure.pressure or 0.0,
                "_umap_options": {
                    "color": "Red",
                    "popupTemplate": "Table",
                }
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(station.lon),
                    float(station.lat)
                ]
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })
