Aereni Backend
==============

## Public API Endpoints

### `/inventory/stations`

Return the list of all the stations.

### `/inventory/stations/<id>`

Return the informations related to a specific station

Parameters :
- `id` : id of the station.

### `/stats/average`

Return the average measures of all the stations.

Parameters :
- `production` (`true` or `false`) : station category to use. Default `true`.

### `/stats/last_measurement`

Return the last single measurement of all the stations.

Parameters :
- `production` (`true` or `false`) : station category to use. `true` by default.

### `/stats/history/<id>`

Return the last measurements of one specific station.

Parameters :
- `id` : id of the station.

### `/stats/last_measurement_umap`

Same as `/stats/last_measurement` but compatible with the [umap library plateform](https://umap.openstreetmap.fr/fr/).

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
