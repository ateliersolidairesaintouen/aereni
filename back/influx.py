from flask_influxdb import InfluxDB

from back.models import DataPoint, Station

influx = InfluxDB()


def write(p: DataPoint, s: Station):
    tags = {
        "esp_id": s.esp_id,
        "aereni_id": s.aereni_id,
        "node_id": s.node_id,
        "indoor": s.indoor,
        "production": s.production,
        "user": s.user,
    }
    influx.write_points([
        {
            "measurement": "production" if s.production else "test",
            "fields": {
                "pm25": p.pm25,
                "pm10": p.pm10,
                "temperature": p.temperature,
                "humidity": p.humidity,
                "pressure": p.pressure
            },
            "tags": tags
        },
        {
            "measurement": "monitoring",
            "fields": {
                "software_version": p.software_version,
                "signal": p.signal,
                "min_micro": p.min_micro,
                "max_micro": p.max_micro,
                "samples": p.samples
            },
            "tags": tags
        }
    ])


def last_average(duration="10m", production=True):
    results = list(
        influx.query(f'SELECT mean(*) FROM {"production" if production else "test"} WHERE time > now() - {duration}').get_points()
    )

    if len(results) == 0:
        return {
            'pm25': 0,
            'pm10': 0,
            'humidity': 0,
            'temperature': 0,
            'pressure': 0
        }

    return {
        'pm25': round(results[0]['mean_pm25'], 2),
        'pm10': round(results[0]['mean_pm10'], 2),
        'humidity': round(results[0]['mean_humidity'], 2),
        'temperature': round(results[0]['mean_temperature'], 2),
        'pressure': round(results[0]['mean_pressure'], 2)
    }
