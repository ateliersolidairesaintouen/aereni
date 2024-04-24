maptilersdk.config.apiKey = '0XwnxCtQlK7VSjPiB9Ea';

const map = new maptilersdk.Map({
  container: 'map', // container's id or the HTML element in which the SDK will render the map
  style: maptilersdk.MapStyle.STREETS,
  center: [2.3342069, 48.9105859], // starting position [lng, lat]
  zoom: 14 // starting zoom
});

const marker = new maptilersdk.Marker({
  color: "#FF0000",
}).setLngLat()
