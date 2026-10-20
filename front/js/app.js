const baseurl = 'https://api.aereni.atelierso.fr';

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
        if (this.markers.length > 0) return;

        for (const station of stations) {
            // Une station sans coordonnées ferait planter setLngLat
            if (station.lon == null || station.lat == null) continue;

            const ind = utils.indicator("pm10", station.pm10);
            const [elmnt] = utils.indicatorElement(ind.cloud);

            // Écouteur attaché directement sur l'élément : plus besoin d'id
            elmnt.addEventListener('click', () => {
                station.more(json => this.details.view(json));
            });

            this.markers.push(
                new maptilersdk.Marker({ element: elmnt })
                    .setLngLat([Number(station.lon), Number(station.lat)])
                    .addTo(this.map)
            );
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
        const lgth = list.length;
        // Math.max(1, ...) évite la boucle infinie s'il y a moins de 24 mesures
        const part = Math.max(1, Math.floor(lgth / 24));

        const final = [];
        for (let u = 0; u < lgth; u += part) {
            final.push(list[u]);
        }

        return final.reverse();
    }

    buildChart(canvas, label) {
        return new Chart(canvas, {
            type: "line",
            data: {
                labels: [],
                datasets: [{ label: label, data: [] }]
            }
        });
    }

    view(history) {
        const last_measure = history.data[0];
        if (last_measure == undefined) return;

        const dataset = this.simplifyDataset(history.data);
        const labels = dataset.map(obj => utils.formatDate(obj.date));

        this.DOMContainer.style.display = "block";

        // Résumé
        this.DOMStationName.innerText = history.name;
        this.DOMPm10.innerText = utils.format(last_measure.pm10, " µg/m³");
        this.DOMPm25.innerText = utils.format(last_measure.pm25, " µg/m³");
        this.DOMTemperature.innerText = utils.format(last_measure.temperature, "°C");
        this.DOMHumidity.innerText = utils.format(last_measure.humidity, " %");

        const ind = utils.indicator("pm10", last_measure.pm10);
        this.DOMIndicator.setAttribute("src", ind.img);

        // Graphiques (créés une seule fois, puis mis à jour)
        if (this.pm10Chart == undefined) {
            this.pm10Chart = this.buildChart(this.DOMPm10Chart, "Mesure PM10");
        }
        this.pm10Chart.data.labels = labels;
        this.pm10Chart.data.datasets[0].data = dataset.map(obj => obj.pm10);
        this.pm10Chart.update();

        if (this.pm25Chart == undefined) {
            this.pm25Chart = this.buildChart(this.DOMPm25Chart, "Mesure PM2,5");
        }
        this.pm25Chart.data.labels = labels;
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
        fetch(baseurl + '/stats/history/' + this.id)
            .then(res => {
                if (!res.ok) throw new Error("HTTP " + res.status);
                return res.json();
            })
            .then(json => {
                this.history = json;
                callback(this.history);
            })
            .catch(error => console.log(error));
    }
}

let utils = {
    indicator: (type, value) => {
        const pngs = {
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
        };

        // Valeur absente : on retombe sur le niveau 1 pour ne pas planter
        if (value == null) return pngs.level1;

        if (type == "pm25") {
            if (value < 15) return pngs.level1;
            if (value < 40) return pngs.level2;
            if (value < 65) return pngs.level3;
            if (value < 150) return pngs.level4;
            return pngs.level5;
        }

        if (type == "pm10") {
            if (value < 55) return pngs.level1;
            if (value < 155) return pngs.level2;
            if (value < 255) return pngs.level3;
            if (value < 355) return pngs.level4;
            return pngs.level5;
        }

        return pngs.level1;
    },
    indicatorElement: src => {
        const elmt = new Image(50, 50);
        elmt.src = src;
        elmt.style.cursor = "pointer";
        return [elmt];
    },
    format: (value, suffix) => {
        return value == null ? "n/a" : value + suffix;
    },
    formatDate: (str) => {
        const date = new Date(str * 1000);
        const hour = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return hour + ":" + minutes;
    }
};

let closeDetails = () => {
    cardStation.style.display = "none";
};

let init = () => {
    const details = new Details(
        cardStation,
        indicator,
        stationName,
        pm10,
        pm25,
        temperature,
        humidity,
        pm10Chart,
        pm25Chart
    );

    fetch(baseurl + '/stats/last_measurement?production=true')
        .then(res => {
            if (!res.ok) throw new Error("HTTP " + res.status);
            return res.json();
        })
        .then(json => {
            const stations = json.map(val => new Station(val, details));
            const map = new MapView("0XwnxCtQlK7VSjPiB9Ea", details);
            map.addMarkers(stations);
        })
        .catch(error => console.log(error));
};

init();
