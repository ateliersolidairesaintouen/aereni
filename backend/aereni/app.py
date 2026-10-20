import os

from flask import Flask
from sqlalchemy_utils import database_exists

from aereni.databases import postgresql
from aereni.ingest import ingest_blueprint
from aereni.inventory import inventory_blueprint, setup_inventory
from aereni.stats import stats_blueprint

AERENI_CONFIG = os.environ.get('AERENI_CONFIG', "../aereni.cfg")


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(AERENI_CONFIG)
    app.config['JSON_SORT_KEYS'] = False

    postgresql.init_app(app)
    # Le CORS est géré par nginx : ne pas activer flask_cors ici,
    # sinon les en-têtes Access-Control-* seraient envoyés en double.
    app.register_blueprint(ingest_blueprint)
    app.register_blueprint(stats_blueprint)
    app.register_blueprint(inventory_blueprint)
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if not database_exists(postgresql.engine.url):
            print(f'initialize database {postgresql.engine.url}')
            setup_inventory()
        else:
            print(f'opening database {postgresql.engine.url}')

    # nginx fait le proxy vers 127.0.0.1:5000. On n'écoute plus sur 0.0.0.0, sinon l'API
    # (y compris /ingest et /inventory) serait joignable directement, sans l'authentification
    # basic d'nginx. Pour changer : AERENI_HOST=0.0.0.0
    app.run(
        host=os.environ.get('AERENI_HOST', '127.0.0.1'),
        port=int(os.environ.get('AERENI_PORT', 5000))
    )
