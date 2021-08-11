#! /usr/bin/env python3
#-*- coding: utf-8 -*-

from flask import Flask
from flask_influxdb import InfluxDB
from flask import jsonify


app = Flask(__name__)
app.config.from_pyfile("aereni.cfg")
influx = InfluxDB()


def get_avg(mesure):

    data = influx.query(
        'SELECT last("' + mesure + '") FROM "pm" GROUP BY node'
    )
    nb = len(data)
    value = 0
    for item in data:
        value += item[0]['last']
    avg = value/nb

    return round(avg, 2)


def get_color(value):
    color = None
    if value < 51:
        color = 'rgba( 0, 153, 102,.95)'    # Vert 0-50
    elif value < 101:
        color = 'rgba( 255, 222, 51,.95)'   # Jaune 51-100
    elif value < 151:
        color = 'rgba( 255, 153, 51,.95)'   # Orange 101-150
    elif value < 201:
        color = 'rgba( 204, 0, 51,.95)'     # Rouge 151-200
    elif value < 301:
        color = 'rgba( 102, 0, 153,.95)'    # Violet 201-300
    elif value > 301:
        color = 'rgba( 126, 0, 35,.95)'   # Marron 301+

    return color


@app.route("/avg")
def avg():

    color = None

    sds_p1 = get_avg('SDS_P1')
    color_p1 = get_color(sds_p1)

    sds_p2 = get_avg('SDS_P2')
    color_p2 = get_color(sds_p2)

    return jsonify(pm10={'value':sds_p1, 'color':color_p1},
                   pm25={'value':sds_p2, 'color':color_p2}
                   )

app.run()
