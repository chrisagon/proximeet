<template>
  <section class="section onboarding">
    <OnboardingStepper :steps="steps" :activeIndex="stepIndex">
      <transition name="fade" mode="out-in">
        <div :key="stepIndex" class="step-panel">
          <div v-if="stepIndex === 0" class="step-content">
            <div class="step-hero">
              <div class="step-icon">👋</div>
              <div>
                <h2>Bienvenue {{ user?.first_name || 'chez Proximeet' }}</h2>
                <p>
                  Proximeet vous aide a partager une presence ephemere et trouver
                  des collegues a proximite pour dejeuner.
                </p>
              </div>
            </div>
            <button class="btn" @click="nextStep">Commencer</button>
          </div>

          <div v-else-if="stepIndex === 1" class="step-content">
            <div class="step-hero">
              <div class="step-icon">🥗</div>
              <div>
                <h2>Preferences personnelles</h2>
                <p>Indiquez vos restrictions et choisissez votre niveau de confidentialite.</p>
              </div>
            </div>
            <div class="field">
              <label>Restrictions alimentaires</label>
              <textarea v-model="preferences.dietary_restrictions" rows="3" placeholder="Vegetarien, sans gluten..."></textarea>
            </div>
            <div class="field">
              <label>Niveau de confidentialite</label>
              <div class="radio-grid">
                <label class="radio-card">
                  <input type="radio" value="PRECISE" v-model="preferences.privacy_level" />
                  <div>
                    <strong>Position precise</strong>
                    <p>Votre position exacte est visible pour les collegues.</p>
                  </div>
                </label>
                <label class="radio-card">
                  <input type="radio" value="BUBBLE" v-model="preferences.privacy_level" />
                  <div>
                    <strong>Mode bubble</strong>
                    <p>Votre position est affichee dans une zone de 300 m.</p>
                  </div>
                </label>
              </div>
            </div>
            <p v-if="error" class="mono error">{{ error }}</p>
            <div class="step-actions">
              <button class="btn secondary" @click="previousStep">Precedent</button>
              <div class="actions-right">
                <button class="btn secondary" @click="skipStep">Passer</button>
                <button class="btn" @click="nextStep">Suivant</button>
              </div>
            </div>
          </div>

          <div v-else-if="stepIndex === 2" class="step-content">
            <div class="step-hero">
              <div class="step-icon">📍</div>
              <div>
                <h2>Premiere position</h2>
                <p>Autorisez la geolocalisation pour partager votre premiere presence.</p>
              </div>
            </div>

            <div class="geo-status">
              <span v-if="geolocating">Detection en cours...</span>
              <span v-else-if="hasCoords(location.latitude, location.longitude)">Position detectee.</span>
              <span v-else>Position non definie.</span>
            </div>
            <button class="btn secondary" @click="detectLocation" :disabled="geolocating">
              {{ geolocating ? 'Localisation...' : 'Detecter ma position' }}
            </button>
            <p v-if="geoError" class="mono error">{{ geoError }}</p>

            <div class="field-grid">
              <div class="field">
                <label>Latitude</label>
                <input v-model.number="location.latitude" type="number" step="0.0001" />
              </div>
              <div class="field">
                <label>Longitude</label>
                <input v-model.number="location.longitude" type="number" step="0.0001" />
              </div>
              <div class="field">
                <label>Type de localisation</label>
                <select v-model="location.location_type">
                  <option value="CLIENT">Client</option>
                  <option value="HOME">Home</option>
                </select>
              </div>
            </div>
            <p v-if="error" class="mono error">{{ error }}</p>
            <div class="step-actions">
              <button class="btn secondary" @click="previousStep">Precedent</button>
              <div class="actions-right">
                <button class="btn secondary" @click="skipStep">Passer</button>
                <button class="btn" @click="nextStep">Suivant</button>
              </div>
            </div>
          </div>

          <div v-else class="step-content">
            <div class="step-hero">
              <div class="step-icon">🧭</div>
              <div>
                <h2>Decouverte</h2>
                <p>Voici les collegues detectes dans un rayon de 2 km.</p>
              </div>
            </div>
            <div class="map-card">
              <ProximeetMap
                :center="mapCenter"
                :zoom="mapZoom"
                :markers="mapMarkers"
              />
            </div>
            <div v-if="nearby.length" class="card-grid" style="margin-top:1rem;">
              <div class="card" v-for="person in nearby" :key="person.user_id">
                <strong>{{ person.first_name || person.nickname || person.user_id }}</strong>
                <p class="mono">{{ person.distance_km }} km</p>
                <p class="mono">{{ person.privacy_level }}</p>
              </div>
            </div>
            <p v-else class="mono">Aucun collegue detecte pour le moment.</p>
            <div class="step-actions">
              <button class="btn secondary" @click="previousStep">Precedent</button>
              <button class="btn" @click="completeOnboarding">Terminer</button>
            </div>
          </div>
        </div>
      </transition>
    </OnboardingStepper>
  </section>
</template>

<script setup lang="ts">
const api = useApi();
const router = useRouter();

const steps = [
  { title: "Bienvenue", subtitle: "Faites connaissance" },
  { title: "Preferences", subtitle: "Vos habitudes" },
  { title: "Position", subtitle: "Partage initial" },
  { title: "Decouverte", subtitle: "Collegues proches" }
];

const stepIndex = ref(0);
const user = ref<any>(null);
const error = ref<string | null>(null);

const preferences = reactive({
  dietary_restrictions: "",
  privacy_level: "BUBBLE"
});

const location = reactive({
  latitude: 0,
  longitude: 0,
  location_type: "CLIENT"
});

const geolocating = ref(false);
const geoError = ref<string | null>(null);
const nearby = ref<any[]>([]);
const mapZoom = 13;
const bubbleRadiusMeters = 300;

const hasCoords = (lat?: number | null, lng?: number | null) => {
  if (typeof lat !== "number" || typeof lng !== "number") return false;
  return !(lat === 0 && lng === 0);
};

const mapCenter = computed<[number, number]>(() => {
  if (hasCoords(location.latitude, location.longitude)) {
    return [location.latitude, location.longitude];
  }
  if (nearby.value.length && hasCoords(nearby.value[0].latitude, nearby.value[0].longitude)) {
    return [nearby.value[0].latitude, nearby.value[0].longitude];
  }
  return [48.8566, 2.3522];
});

const mapMarkers = computed(() => {
  const markers: any[] = [];
  if (hasCoords(location.latitude, location.longitude)) {
    markers.push({
      id: "self",
      lat: location.latitude,
      lng: location.longitude,
      type: "self",
      popupTitle: "Votre position",
      popupLines: [location.location_type]
    });
  }

  nearby.value.forEach((person) => {
    if (!hasCoords(person.latitude, person.longitude)) return;
    markers.push({
      id: person.user_id,
      lat: person.latitude,
      lng: person.longitude,
      type: "colleague",
      popupTitle: person.first_name || person.nickname || person.user_id,
      popupLines: [`${person.distance_km} km`, person.privacy_level],
      bubbleRadiusMeters: person.privacy_level === "BUBBLE" ? bubbleRadiusMeters : 0
    });
  });

  return markers;
});

const loadUser = async () => {
  try {
    user.value = await api.get("/me");
  } catch (err: any) {
    error.value = err?.message || "Impossible de charger le profil";
  }
};

const hydratePreferences = () => {
  if (!process.client) return;
  const stored = localStorage.getItem("user_preferences");
  if (!stored) return;
  try {
    const parsed = JSON.parse(stored);
    if (parsed?.dietary_restrictions) preferences.dietary_restrictions = parsed.dietary_restrictions;
    if (parsed?.privacy_level) preferences.privacy_level = parsed.privacy_level;
  } catch {
    // ignore parsing errors
  }
};

const detectLocation = () => {
  geoError.value = null;
  if (!process.client) {
    geoError.value = "Geolocalisation disponible uniquement cote client";
    return;
  }
  if (!navigator.geolocation) {
    geoError.value = "Geolocalisation non supportee";
    return;
  }
  geolocating.value = true;
  navigator.geolocation.getCurrentPosition(
    (position) => {
      location.latitude = position.coords.latitude;
      location.longitude = position.coords.longitude;
      geolocating.value = false;
    },
    (err) => {
      geoError.value = `Erreur geolocalisation: ${err.message}`;
      geolocating.value = false;
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
  );
};

const savePreferences = async () => {
  error.value = null;
  await api.patch("/me", {
    dietary_restrictions: preferences.dietary_restrictions || undefined,
    privacy_level: preferences.privacy_level
  });
  if (process.client) {
    localStorage.setItem("user_preferences", JSON.stringify({
      dietary_restrictions: preferences.dietary_restrictions,
      privacy_level: preferences.privacy_level
    }));
  }
};

const sharePresence = async () => {
  error.value = null;
  if (!hasCoords(location.latitude, location.longitude)) {
    throw new Error("Position requise");
  }
  await api.post("/presence", {
    latitude: location.latitude,
    longitude: location.longitude,
    location_type: location.location_type,
    expires_in_hours: 6
  });
};

const loadNearby = async () => {
  try {
    nearby.value = await api.get("/nearby?radius_km=2");
  } catch (err) {
    nearby.value = [];
  }
};

const nextStep = async () => {
  error.value = null;
  try {
    if (stepIndex.value === 1) {
      await savePreferences();
    }
    if (stepIndex.value === 2) {
      await sharePresence();
    }
    if (stepIndex.value < steps.length - 1) {
      stepIndex.value += 1;
    }
    if (stepIndex.value === 3) {
      await loadNearby();
    }
  } catch (err: any) {
    error.value = err?.message || "Impossible de continuer";
  }
};

const previousStep = () => {
  if (stepIndex.value > 0) stepIndex.value -= 1;
};

const skipStep = () => {
  error.value = null;
  if (stepIndex.value < steps.length - 1) {
    stepIndex.value += 1;
  }
  if (stepIndex.value === 3) {
    loadNearby();
  }
};

const completeOnboarding = async () => {
  if (process.client) {
    localStorage.setItem("onboarding_completed", "true");
  }
  await router.push("/dashboard");
};

onMounted(async () => {
  if (process.client) {
    const completed = localStorage.getItem("onboarding_completed");
    if (completed === "true") {
      router.replace("/dashboard");
      return;
    }
  }
  hydratePreferences();
  await loadUser();
});
</script>

<style scoped>
.onboarding {
  display: grid;
  gap: 2rem;
}

.step-panel {
  display: grid;
  gap: 1.5rem;
}

.step-content {
  display: grid;
  gap: 1.5rem;
}

.step-hero {
  display: flex;
  gap: 1.2rem;
  align-items: center;
  background: rgba(86, 163, 166, 0.12);
  padding: 1.4rem;
  border-radius: 18px;
  border: 1px solid rgba(15, 27, 45, 0.08);
}

.step-icon {
  font-size: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: #ffffff;
  box-shadow: 0 10px 20px var(--shadow);
}

.radio-grid {
  display: grid;
  gap: 0.8rem;
}

.radio-card {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  padding: 0.9rem;
  border-radius: 14px;
  border: 1px solid rgba(15, 27, 45, 0.1);
  background: rgba(255, 255, 255, 0.8);
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.geo-status {
  font-weight: 600;
  color: var(--sea);
}

.map-card {
  border-radius: 20px;
  overflow: hidden;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.actions-right {
  display: flex;
  gap: 0.8rem;
}

.error {
  color: var(--accent);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
