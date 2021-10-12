#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from back import influx
from back.inventory import get_station
from back.models import parse_esp_json

app = Flask(__name__)
app.config.from_pyfile("aereni.cfg")
CORS(app)


@app.post("/ingest")
def ingest():
    print(request.data)
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    data_point = parse_esp_json(request.json)
    station = get_station(data_point.esp_id)
    influx.write(data_point, station)

    return jsonify({"status": "success"})


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


@app.get("/stats/average")
def average():
    production = request.args.get('production', True, type=lambda v: v.lower() == 'true')
    measures = influx.last_average(production=production)
    return jsonify({
        'measures': measures,
        'colors': {
            'pm25': pm_color(measures['pm25']),
            'pm10': pm_color(measures['pm10'])
        }
    })


app.run(host='0.0.0.0')
