Aereni Backend
==============

## Development setup

Requirements :
- python >= 3.6 (tested with 3.10)
- pip and virtualenv
- influxdb 1.8

Create / load virtualenv :

    virtualenv -p $(which python3.10) venv
    source venv/bin/activate

Download dependencies :

    pip install -r requirements.txt

Create / update configuration file :

    cp aereni.cfg.example aereni.cfg
    vim aereni.cfg

Start the server :

     python -m aereni.app
