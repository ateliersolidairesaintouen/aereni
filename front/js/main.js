maptilersdk.config.apiKey = '0XwnxCtQlK7VSjPiB9Ea';

// Left panel

const nav = document.getElementById("nav");
const content = document.getElementById("content");
const mapDiv = document.getElementById("map");
const cardStation = document.getElementById("card-station");

// Measures DOM elements
const indicator = document.getElementById("indicator");
const stationName = document.getElementById("stationName");
const pm10 = document.getElementById("pm10");
const pm25 = document.getElementById("pm25");
const temperature = document.getElementById("temperature");
const humidity = document.getElementById("humidity");

var formatDate = (str) => {
  var date = new Date(str);
  var hour = date.getHours();
  var minutes = date.getMinutes();
  console.log(date, hour, minutes);
  return hour + ":" + minutes;
}

var getIndicator = (type, value) => {
  var pngs = {
    level1: "/assets/good.png",
    level2: "/assets/ok.png",
    level3: "/assets/bof.png",
    level4: "/assets/bad.png",
    level5: "/assets/verybad.png"
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
}

var simplifyDataset = (list) => {
  var lgth = list.length;
  var part = Math.floor(lgth / 24);

  var u = 0;
  var final = [];
  while (u < lgth - 1) {
    final.push(list[u]);
    u += part;
  }

  final.push(list[lgth - 1])

  return final;
}

var treatData = (map, last, history) => {
  var dataset = simplifyDataset(history.data);

  stationName.innerText = last.name;
  pm10.innerText = last.pm10 + " µg/m³";
  pm25.innerText = last.pm25 + " µg/m³";
  temperature.innerText = last.temperature + "°C";
  humidity.innerText = last.humidity + " %";

  indicator.setAttribute("src", getIndicator("pm10", last.pm10))

  const marker = new maptilersdk.Marker()
    .setLngLat([last.lon, last.lat])
    .addTo(map);

  const pm10Chart = new Chart(
      document.getElementById("pm10-chart"),
      {
        type: "line",
        data: {
          labels: dataset.map(obj => formatDate(obj.date)),
          datasets: [
            {
              label: "Mesure PM10",
              data: dataset.map(obj => obj.pm10)
            }
          ]
        }
      }
    );

  const pm125hart = new Chart(
    document.getElementById("pm25-chart"),
    {
      type: "line",
      data: {
        labels: dataset.map(obj => formatDate(obj.date)),
        datasets: [
          {
            label: "Mesure PM25 ",
            data: dataset.map(obj => obj.pm25)
          }
        ]
      }
    }
  );
};

var about = () => {

};

var mapHeight = () => {
  var windowHeight = window.innerHeight;
  var navHeight = nav.offsetHeight;
  mapDiv.style.height = (windowHeight - navHeight) + "px";
  cardStation.style.height = "calc(" + (windowHeight - navHeight) + "px - 2em";
  console.log(windowHeight - navHeight)
};

window.addEventListener('load', mapHeight);
window.addEventListener('resize', mapHeight);

const map = new maptilersdk.Map({
  container: 'map', // container's id or the HTML element in which the SDK will render the map
  style: maptilersdk.MapStyle.STREETS,
  center: [2.3342069, 48.9105859], // starting position [lng, lat]
  zoom: 14 // starting zoom
});

// CHARTS

async function update() {
  var last = await (await fetch('https://api.aereni.atelierso.fr/stats/last_measurement?production=true')).json();
  var history = await (await fetch('https://api.aereni.atelierso.fr/stats/history/14')).json();
  treatData(map, last[0], history);
}

update();
