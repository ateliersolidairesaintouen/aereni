import os

from flask import Flask
from flask_cors import CORS
from sqlalchemy_utils import database_exists

from aereni.databases import sqlite, influx
from aereni.ingest import ingest_blueprint
from aereni.inventory import inventory_blueprint, setup_inventory
from aereni.stats import stats_blueprint

AERENI_CONFIG = os.environ.get('AERENI_CONFIG', "../aereni.cfg")


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(AERENI_CONFIG)
    sqlite.init_app(app)
    influx.init_app(app)
    CORS(app, expose_headers=['X-Total-Count', 'Authorization'], supports_credentials=True)
    app.register_blueprint(ingest_blueprint)
    app.register_blueprint(stats_blueprint)
    app.register_blueprint(inventory_blueprint)
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if not database_exists(sqlite.engine.url):
            print(f'initialize database {sqlite.engine.url}')
            setup_inventory()
    app.run(host='0.0.0.0')
