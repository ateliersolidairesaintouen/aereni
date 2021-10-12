from decimal import Decimal

from back.models import Station

# TODO: store this in an external database
sensor_info_index = {
    '15002893': Station(aereni_id='11', esp_id='15002893',
                        indoor=True, production=False,
                        node_id="chez barth",
                        user='barth', address="XXXXX",
                        lat=Decimal(42), lon=Decimal(42), floor=5),
    'test1': Station(aereni_id='test1', esp_id='test1',
                     indoor=True, production=False,
                     node_id="test1",
                     user='test1', address="test1",
                     lat=Decimal(42), lon=Decimal(42), floor=5)
}


def get_station(esp_id: str) -> Station:
    # TODO: get from an external database
    return sensor_info_index.get(esp_id, None)
