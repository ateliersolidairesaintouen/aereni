const baseurl = 'https://api.aereni.atelierso.fr'

const cardStation = document.getElementById("station");
const indicator = document.getElementById("indicator");
const stationName = document.getElementById("stationName");
const pm10 = document.getElementById("pm10");
const pm25 = document.getElementById("pm25");
const pm10Chart = document.getElementById("pm10-chart");
const pm25Chart = document.getElementById("pm25-chart");
const temperature = document.getElementById("temperature");
const humidity = document.getElementById("humidity");

class MapView {
    constructor(apikey, details) {
        maptilersdk.config.apiKey = apikey;
        this.details = details;
        this.markers = [];
        this.map = new maptilersdk.Map({
            container: 'map',
            style: maptilersdk.MapStyle.STREETS,
            center: [2.3342069, 48.9105859],
            zoom: 14
        }).setMinZoom(13);
    }

    addMarkers(stations) {
        if (this.markers.length == 0) {
            for (var i = 0; i < stations.length; ++i) {
                var station = stations[i];
                console.log(station)
                var ind = utils.indicator("pm10", station.pm10);
                this.markers.push(new maptilersdk.Marker({
                    element: utils.indicatorElement(ind.cloud, () => {
                        station.more(json => this.details.view(json))
                    })
                }).setLngLat([station.lon, station.lat]).addTo(this.map));
            }
        }
    }
}

class Details {
    constructor(
        container,
        indicator,
        stationName,
        pm10,
        pm25,
        temperature,
        humidity,
        pm10Chart,
        pm25Chart
    ) {
        this.DOMContainer = container;
        this.DOMIndicator = indicator;
        this.DOMStationName = stationName;
        this.DOMPm10 = pm10;
        this.DOMPm25 = pm25;
        this.DOMTemperature = temperature;
        this.DOMHumidity = humidity;
        this.DOMPm10Chart = pm10Chart;
        this.DOMPm25Chart = pm25Chart;
    }

    simplifyDataset(list) {
        var lgth = list.length;
        var part = Math.floor(lgth / 24);

        var u = 0;
        var final = [];
        while (u < lgth) {
            final.push(list[u]);
            u += part;
        }

        return final.reverse();
    }

    view(history) {
        var dataset = this.simplifyDataset(history.data);
        var last_measure = history.data[0];

        if (last_measure == undefined) return;
        this.DOMContainer.style.display = "block";

        // Treating sum up informations
        this.DOMStationName.innerText = history.name;
        this.DOMPm10.innerText = last_measure.pm10 + " µg/m³";
        this.DOMPm25.innerText = last_measure.pm25 + " µg/m³";
        this.DOMTemperature.innerText = last_measure.temperature + "°C";
        this.DOMTemperature.innerText = last_measure.humidity + " %";

        var ind = utils.indicator("pm10", last_measure.pm10);
        this.DOMIndicator.setAttribute("src", ind.img);

        // Treating charts
        if (this.pm10Chart == undefined) {
            this.pm10Chart = new Chart(this.DOMPm10Chart, {
                type: "line",
                data: {
                    labels: dataset.map(obj => utils.formatDate(obj.date)),
                    datasets: [
                        {
                            label: "Mesure PM10",
                            data: []
                        }
                    ]
                }
                }
            );
        }

        this.pm10Chart.data.datasets[0].data = dataset.map(obj => obj.pm10);
        this.pm10Chart.update();

        if (this.pm25Chart == undefined) {
            this.pm25Chart = new Chart(this.DOMPm25Chart, {
                type: "line",
                data: {
                    labels: dataset.map(obj => utils.formatDate(obj.date)),
                    datasets: [
                        {
                            label: "Mesure PM2,5 ",
                            data: []
                        }
                    ]
                }
                }
            );
        }

        this.pm25Chart.data.datasets[0].data = dataset.map(obj => obj.pm25);
        this.pm25Chart.update();
    }
}

class Station {
    constructor(last_measurement, details) {
        this.id = last_measurement.id;
        this.esp_id = last_measurement.esp_id;
        this.name = last_measurement.name;
        this.lon = last_measurement.lon;
        this.lat = last_measurement.lat;
        this.pm25 = last_measurement.pm25;
        this.pm10 = last_measurement.pm10;
        this.humidity = last_measurement.humidity;
        this.temperature = last_measurement.temperature;
        this.pressure = last_measurement.pressure;
        this.details = details;
    }

    more(callback) {
        fetch(baseurl + '/stats/history/' + this.id).then(res => {
            res.json().then(json => {
                this.history = json;
                callback(this.history);
            }).catch(error => {
                console.log(error)
            })
        }).catch(error => {
            console.log(error)
        })
    }
}

var utils = {
    indicator: (type, value) => {
        var pngs = {
            level1: {
                img: "/assets/good.png",
                cloud: "/assets/cloud-good.png",
                color: "#53B260"
            },
            level2: {
                img: "/assets/ok.png",
                cloud: "/assets/cloud-ok.png",
                color: "#A2CB76",
            },
            level3: {
                img: "/assets/bof.png",
                cloud: "/assets/cloud-bof.png",
                color: "#FBBD54",
            },
            level4: {
                img: "/assets/bad.png",
                cloud: "/assets/cloud-bad.png",
                color: "#EE733E",
            },
            level5: {
                img: "/assets/verybad.png",
                cloud: "/assets/cloud-verybad.png",
                color: "#E63C34",
            }
        }

        if (type == "pm25") {
            if (value < 15) {
                return pngs.level1;
            } else if (15 <= value && value < 40) {
                return pngs.level2;
            } else if (40 <= value && value < 65) {
                return pngs.level3;
            } else if (65 <= value && value < 150) {
                return pngs.level4;
            } else if (150 <= value) {
                return pngs.level5;
            }
            } else if (type == "pm10") {
            if (value < 55) {
                return pngs.level1;
            } else if (55 <= value && value < 155) {
                return pngs.level2;
            } else if (155 <= value && value < 255) {
                return pngs.level3;
            } else if (255 <= value && value < 355) {
                return pngs.level4;
            } else if (355 <= value) {
                return pngs.level5;
            }
        }
    },
    indicatorElement: (src, click) => {
        let elmt = new Image(50, 50);
        elmt.src = src;
        elmt.addEventListener('click', _ => click())
        return elmt;
    },
    formatDate: (str) => {
        var date = new Date(str * 1000);
        var hour = new String(date.getHours()).padStart(2, '0');
        var minutes = new String(date.getMinutes()).padStart(2, '0');
        return hour + ":" + minutes;
    }
}

var closeDetails = () => {
    cardStation.style.display = "none";
}

var init = () => {
    var details = new Details(
        cardStation,
        indicator,
        stationName,
        pm10,
        pm25,
        temperature,
        humidity,
        pm10Chart,
        pm25Chart
    )
    fetch(baseurl + '/stats/last_measurement?production=true').then(res => {
        res.json().then(json => {
            var stations = json.map(val => new Station(val, details));
            var map = new MapView("0XwnxCtQlK7VSjPiB9Ea", details);
            console.log(stations)
            map.addMarkers(stations);
        }).catch(error => console.log(error))
    }).catch(error => console.log(error))
}

init()
