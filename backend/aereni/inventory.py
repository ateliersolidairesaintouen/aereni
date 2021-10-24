from dataclasses import dataclass

from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError

from aereni.databases import sqlite

inventory_blueprint = Blueprint('inventory', __name__)


@dataclass
class Station(sqlite.Model):
    __tablename__ = 'station'

    # uniquely identify a station
    id: str = sqlite.Column(sqlite.String, primary_key=True)

    # name of the Station
    name: str = sqlite.Column(sqlite.String, unique=True, nullable=False)

    # esp_id depends on the current esp installed in the station, it can vary if we replace the esp after a failure
    esp_id: str = sqlite.Column(sqlite.String, unique=True, nullable=False)

    # sensebox_id as defined in opensensemap platform
    sensebox_id: str = sqlite.Column(sqlite.String, unique=True, nullable=True)

    # a node_id uniquely identify a location where we installed a station
    node_id: str = sqlite.Column(sqlite.String, unique=True, nullable=True)

    # identify the owner of the node (!= owner of the Station)
    user: str = sqlite.Column(sqlite.String, unique=False, nullable=True)
    address: str = sqlite.Column(sqlite.String, unique=False, nullable=True)
    floor: int = sqlite.Column(sqlite.Integer, unique=False, nullable=True)
    lat: float = sqlite.Column(sqlite.Numeric, unique=False, nullable=True)
    lon: float = sqlite.Column(sqlite.Numeric, unique=False, nullable=True)
    indoor: bool = sqlite.Column(sqlite.Boolean, unique=False, nullable=True)

    # if true, the data-points emitted by the station are considered real
    production: bool = sqlite.Column(sqlite.Boolean, unique=False, nullable=False, default=False)

    # identify the owner of the station (e.g atso, ben...)
    owner: str = sqlite.Column(sqlite.String, unique=False, nullable=False, default="ATSO")

    def __repr__(self):
        return '<Station %r>' % self.name


def setup_inventory():
    sqlite.create_all()
    #### test data ###
    s1 = Station(
        name='Station 11',
        id='11', esp_id='15002893',
        indoor=True, production=False,
        node_id="3435468416864",
        user='barth', address="XXXXX",
        lat=42.0, lon=42.0, floor=5
    )
    sqlite.session.add(s1)
    sqlite.session.commit()


def get_station_by_esp_id(esp_id: str) -> Station:
    return sqlite.session.query(Station).filter_by(esp_id=esp_id).first()


@inventory_blueprint.get("/inventory/stations")
def api_list_stations():
    all_stations = sqlite.session.query(Station).all()
    resp = make_response(jsonify(all_stations))
    resp.headers['X-Total-Count'] = len(all_stations)
    return resp


@inventory_blueprint.get("/inventory/stations/<id>")
def api_get_station(id: str):
    station = sqlite.session.query(Station).get(id)
    if station is None:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404
    return jsonify(station)


@inventory_blueprint.post("/inventory/stations")
def api_create_station():
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    try:
        station = Station(**request.json)
        sqlite.session.add(station)
        sqlite.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400

    return jsonify(station)


@inventory_blueprint.patch("/inventory/stations/<id>")
def api_partial_update_station(id: str):
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    station = sqlite.session.query(Station).get(id)
    if station is None:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404

    for key, value in request.json.items():
        if not hasattr(station, key):
            return jsonify({"error": 400, "message": f"Station has no attribute '{key}'"})
        setattr(station, key, value)

    try:
        sqlite.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400

    return jsonify(station)


@inventory_blueprint.delete("/inventory/stations/<id>")
def api_delete_station(id: str):
    count = Station.query.filter_by(id=id).delete()
    if count == 0:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404
    try:
        sqlite.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400
    return jsonify({"status": "success"})
