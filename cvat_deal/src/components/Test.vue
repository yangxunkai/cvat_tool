<template>
  <div>
    <div id="map" class="map"></div>
    <div class="controls">
      <button @click="setDestination('Shanghai')">导航到上海</button>
      <button @click="setDestination('Beijing')">导航到北京</button>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';
import 'leaflet-control-geocoder';
import 'leaflet-control-geocoder/dist/Control.Geocoder.css';

export default {
  name: 'MapC',
  data() {
    return {
      map: null,
      routingControl: null,
      currentLocation: null,
    };
  },
  mounted() {
    this.initMap();
    this.getCurrentLocation();
  },
  methods: {
    initMap() {
      this.map = L.map('map').setView([39.9, 116.4], 5); // 默认位置为北京

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);
    },
    getCurrentLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          this.currentLocation = L.latLng(lat, lng);
          this.setCurrentLocation(lat, lng);
        }, () => {
          alert("无法获取您的位置");
        });
      } else {
        alert("浏览器不支持定位");
      }
    },
    setCurrentLocation(lat, lng) {
      L.marker([lat, lng]).addTo(this.map).bindPopup('当前位置').openPopup();
      this.map.setView([lat, lng], 13); // 将地图中心设为当前位置
    },
    setDestination(city) {
      let destination;
      if (city === 'Shanghai') {
        destination = L.latLng(31.2304, 121.4737);
      } else if (city === 'Beijing') {
        destination = L.latLng(39.9042, 116.4074);
      }

      // 清除之前的路线
      if (this.routingControl) {
        this.routingControl.remove();
      }

      // 添加路线
      this.routingControl = L.Routing.control({
        waypoints: [
          this.currentLocation,
          destination
        ],
        routeWhileDragging: true,
        geocoder: L.Control.Geocoder.nominatim(), // 使用Nominatim Geocoder
      }).addTo(this.map);
    },
  },
};
</script>

<style>
.map {
  height: 500px;
  width: 100%;
}
.controls {
  margin: 10px 0;
}
</style>
