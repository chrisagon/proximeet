<template>
  <div class="proximeet-map">
    <ClientOnly>
      <LMap
        :center="center"
        :zoom="zoom"
        class="proximeet-map__canvas"
        @click="handleMapClick"
      >
        <LTileLayer :url="tileUrl" :attribution="tileAttribution" />

        <template v-if="isReady">
          <LCircle
            v-for="marker in bubbleMarkers"
            :key="`${marker.id}-bubble`"
            :lat-lng="[marker.lat, marker.lng]"
            :radius="marker.bubbleRadiusMeters"
            :color="bubbleColor(marker)"
            :fill-color="bubbleColor(marker)"
            :fill-opacity="0.18"
            :opacity="0.45"
          />

          <LMarker
            v-for="marker in markers"
            :key="marker.id"
            :lat-lng="[marker.lat, marker.lng]"
            :icon="iconFor(marker)"
            @click="() => handleMarkerClick(marker)"
          >
            <LPopup v-if="marker.popupTitle || marker.popupLines">
              <div class="proximeet-popup">
                <strong v-if="marker.popupTitle">{{ marker.popupTitle }}</strong>
                <p v-for="(line, index) in marker.popupLines" :key="index" class="proximeet-popup__line">
                  {{ line }}
                </p>
              </div>
            </LPopup>
          </LMarker>
        </template>
      </LMap>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { LCircle, LMap, LMarker, LPopup, LTileLayer } from "@vue-leaflet/vue-leaflet";

type ProximeetMarker = {
  id: string;
  lat: number;
  lng: number;
  type?: "self" | "colleague" | "restaurant";
  popupTitle?: string;
  popupLines?: string[];
  bubbleRadiusMeters?: number;
};

const props = defineProps<{
  center: [number, number];
  zoom: number;
  markers: ProximeetMarker[];
}>();

const emit = defineEmits<{
  (e: "marker-click", marker: ProximeetMarker): void;
  (e: "map-click", latlng: { lat: number; lng: number }): void;
}>();

const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const tileAttribution = "&copy; OpenStreetMap contributors";

const isReady = ref(false);
let createDivIcon: ((options: any) => any) | null = null;

onMounted(async () => {
  // Charger le CSS de Leaflet dynamiquement
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
  link.crossOrigin = '';
  document.head.appendChild(link);
  
  const leaflet = await import("leaflet");
  createDivIcon = leaflet.divIcon;
  isReady.value = true;
});

const bubbleMarkers = computed(() =>
  props.markers.filter((marker) => (marker.bubbleRadiusMeters || 0) > 0)
);

const iconFor = (marker: ProximeetMarker) => {
  const type = marker.type || "default";
  if (!createDivIcon) return undefined;
  return createDivIcon({
    className: `proximeet-marker-icon proximeet-marker-${type}`,
    html: "<span class='proximeet-marker-dot'></span>",
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

const bubbleColor = (marker: ProximeetMarker) => {
  if (marker.type === "self") return "#4a90e2";
  if (marker.type === "restaurant") return "#ff7a59";
  return "#2f9e44";
};

const handleMarkerClick = (marker: ProximeetMarker) => {
  emit("marker-click", marker);
};

const handleMapClick = (event: any) => {
  if (event?.latlng) {
    emit("map-click", { lat: event.latlng.lat, lng: event.latlng.lng });
  }
};
</script>

<style>
.proximeet-map {
  width: 100%;
  height: 360px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(15, 27, 45, 0.08);
  box-shadow: 0 14px 28px var(--shadow);
}

.proximeet-map__canvas,
.proximeet-map__canvas .leaflet-container {
  height: 100%;
  width: 100%;
}

.proximeet-marker-icon {
  background: transparent;
  border: none;
}

.proximeet-marker-dot {
  display: block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #ffffff;
  background: var(--accent);
  box-shadow: 0 8px 18px rgba(15, 27, 45, 0.35);
  animation: markerPop 0.3s ease;
}

.proximeet-marker-self .proximeet-marker-dot {
  background: #4a90e2;
}

.proximeet-marker-colleague .proximeet-marker-dot {
  background: #2f9e44;
}

.proximeet-marker-restaurant .proximeet-marker-dot {
  background: var(--accent);
}

.proximeet-popup {
  min-width: 140px;
}

.proximeet-popup__line {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--ink);
}

@keyframes markerPop {
  from {
    transform: scale(0.6);
    opacity: 0.6;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
