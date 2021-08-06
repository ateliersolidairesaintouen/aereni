#! /usr/bin/env python3
#-*- coding: utf-8 -*-

from flask import Flask
from flask_influxdb import InfluxDB
from flask import jsonify

app = Flask(__name__)
app.config.from_pyfile("aereni.cfg")
influx = InfluxDB()

@app.route("/avg")
def avg():

    #tabledata = 'ok'
    data10 = influx.query(
        'SELECT last("SDS_P1") FROM "pm" GROUP BY node'
    )
    data25 = influx.query(
        'SELECT last("SDS_P2") FROM "pm" GROUP BY node'
    )

    nb10 = len(data10)
    value10 = 0
    for item in data10:
        value10 += item[0]['last']
    avg10 = value10/nb10

    nb25 = len(data25)
    value25 = 0
    for item in data25:
        value25 += item[0]['last']
    avg25 = value25/nb25

    return jsonify(pm10=avg10, pm25=avg25)

app.run()
