from dataclasses import dataclass

from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError

from aereni.databases import postgresql

inventory_blueprint = Blueprint('inventory', __name__)


@dataclass
class Station(postgresql.Model):
    __tablename__ = 'station'

    # uniquely identify a station
    id: str = postgresql.Column(postgresql.String, primary_key=True)

    # name of the Station
    name: str = postgresql.Column(postgresql.String, unique=True, nullable=False)

    # esp_id depends on the current esp installed in the station, it can vary if we replace the esp after a failure
    esp_id: str = postgresql.Column(postgresql.String, unique=True, nullable=False)

    # sensebox_id as defined in opensensemap platform
    sensebox_id: str = postgresql.Column(postgresql.String, unique=True, nullable=True)

    # a node_id uniquely identify a location where we installed a station
    node_id: str = postgresql.Column(postgresql.String, unique=True, nullable=True)

    # identify the owner of the node (!= owner of the Station)
    user: str = postgresql.Column(postgresql.String, unique=False, nullable=True)
    address: str = postgresql.Column(postgresql.String, unique=False, nullable=True)
    floor: int = postgresql.Column(postgresql.Integer, unique=False, nullable=True)
    lat: float = postgresql.Column(postgresql.Numeric, unique=False, nullable=True)
    lon: float = postgresql.Column(postgresql.Numeric, unique=False, nullable=True)
    indoor: bool = postgresql.Column(postgresql.Boolean, unique=False, nullable=True)

    # if true, the data-points emitted by the station are considered real
    production: bool = postgresql.Column(postgresql.Boolean, unique=False, nullable=False, default=False)

    # identify the owner of the station (e.g atso, ben...)
    owner: str = postgresql.Column(postgresql.String, unique=False, nullable=False, default="ATSO")

    comment: str = postgresql.Column(postgresql.String, unique=False, nullable=True, default="")

    def __repr__(self):
        return '<Station %r>' % self.name


def setup_inventory():
    postgresql.create_all()
    postgresql.session.commit()


def get_station_by_esp_id(esp_id: str) -> Station:
    return postgresql.session.query(Station).filter_by(esp_id=esp_id).first()

def get_station_by_id(id: str) -> Station:
    return postgresql.session.query(Station).filter_by(id=id).first()

@inventory_blueprint.get("/inventory/stations")
def api_list_stations():
    all_stations = postgresql.session.query(Station).all()
    resp = make_response(jsonify(all_stations))
    resp.headers['X-Total-Count'] = len(all_stations)
    return resp


@inventory_blueprint.get("/inventory/stations/<id>")
def api_get_station(id: str):
    station = postgresql.session.query(Station).get(id)
    if station is None:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404
    return jsonify(station)


@inventory_blueprint.post("/inventory/stations")
def api_create_station():
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    try:
        station = Station(**request.json)
        postgresql.session.add(station)
        postgresql.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400

    return jsonify(station)


@inventory_blueprint.patch("/inventory/stations/<id>")
def api_partial_update_station(id: str):
    if not request.is_json:
        return jsonify({"error": 400, "message": "Invalid request"}), 400

    station = postgresql.session.query(Station).get(id)
    if station is None:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404

    for key, value in request.json.items():
        if not hasattr(station, key):
            return jsonify({"error": 400, "message": f"Station has no attribute '{key}'"})
        setattr(station, key, value)

    try:
        postgresql.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400

    return jsonify(station)


@inventory_blueprint.delete("/inventory/stations/<id>")
def api_delete_station(id: str):
    count = Station.query.filter_by(id=id).delete()
    if count == 0:
        return jsonify({"error": 404, "message": f"There is no station with id={id}"}), 404
    try:
        postgresql.session.commit()
    except SQLAlchemyError as e:
        return jsonify({"error": 400, "message": str(e)}), 400
    return jsonify({"status": "success"})
