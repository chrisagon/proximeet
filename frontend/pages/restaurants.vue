<template>
  <section class="section">
    <div class="card">
      <h2 class="section-title">Recherche Google Places</h2>
      <div class="field">
        <label>Query</label>
        <input v-model="searchQuery" placeholder="Sushi, brasserie, etc." />
      </div>
      <button class="btn" style="margin-top:1rem;" @click="searchPlaces" :disabled="geolocating">
        {{ geolocating ? 'Localisation...' : 'Rechercher' }}
      </button>
      <p v-if="userLocation.lat" class="mono" style="font-size: 0.8rem; color: #2f9e44; margin-top: 0.5rem;">
        📍 Recherche autour de vous ({{ userLocation.source === 'gps' ? 'GPS' : 'Profil' }})
      </p>
      <div class="card-grid" style="margin-top:1rem;">
        <div class="card" v-for="result in searchResults" :key="result.place_id">
          <strong>{{ result.name }}</strong>
          <p class="mono">{{ result.address }}</p>
          <button class="btn secondary" @click="addRestaurant(result)">Ajouter</button>
        </div>
      </div>
      <p class="mono" v-if="searchMessage">{{ searchMessage }}</p>
    </div>

    <div class="card">
      <h2 class="section-title">Carte des restaurants</h2>
      <ProximeetMap
        :center="restaurantCenter"
        :zoom="restaurantZoom"
        :markers="restaurantMarkers"
        @marker-click="handleRestaurantMarkerClick"
      />
      <p class="mono" style="margin-top:0.8rem;">
        Marqueurs orange: restaurants internes ou issus de la recherche.
      </p>
    </div>

    <div class="card">
      <h2 class="section-title">Mes favoris</h2>
      <button class="btn secondary" @click="loadFavorites">Rafraichir</button>
      <div class="card-grid" style="margin-top:1rem;">
        <div class="card" v-for="favorite in favorites" :key="favorite.restaurant.place_id">
          <strong>{{ favorite.restaurant.name }}</strong>
          <p class="mono">Ajoute le {{ new Date(favorite.created_at).toLocaleDateString() }}</p>
          <button class="btn secondary" @click="toggleFavorite(favorite.restaurant.place_id)">
            Retirer des favoris
          </button>
        </div>
      </div>
      <p class="mono" v-if="favorites.length === 0">Aucun favori pour le moment.</p>
    </div>

    <div class="card">
      <h2 class="section-title">Restaurants internes</h2>
      <button class="btn secondary" @click="loadRestaurants">Rafraichir</button>
      <div class="card-grid" style="margin-top:1rem;">
        <div
          class="card"
          v-for="restaurant in internalRestaurants"
          :key="restaurant.place_id"
          :ref="setRestaurantRef(restaurant.place_id)"
        >
          <strong>{{ restaurant.name }}</strong>
          <p>
            <span class="tag" v-for="tag in tagList(restaurant.cuisine_tags)" :key="tag">{{ tag }}</span>
          </p>
          <p class="mono">Votes: {{ restaurant.vote_count }} | Note: {{ restaurant.average_rating }}</p>
          <div class="field">
            <label>Note</label>
            <select v-model.number="ratings[restaurant.place_id]">
              <option :value="1">1</option>
              <option :value="2">2</option>
              <option :value="3">3</option>
              <option :value="4">4</option>
              <option :value="5">5</option>
            </select>
          </div>
          <div class="field">
            <label>Commentaire</label>
            <textarea v-model="comments[restaurant.place_id]"></textarea>
          </div>
          <button class="btn secondary" @click="toggleFavorite(restaurant.place_id)">
            {{ isFavorite(restaurant.place_id) ? 'Retirer des favoris' : '⭐ Favori' }}
          </button>
          <button class="btn" @click="addRecommendation(restaurant.place_id)">Noter</button>
          <button
            v-if="isAdmin"
            class="btn secondary"
            @click="deleteRestaurant(restaurant.place_id, restaurant.name)"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();
const currentUser = ref<any | null>(null);
const searchQuery = ref("");
const searchResults = ref<any[]>([]);
const searchMessage = ref<string | null>(null);
const restaurants = ref<any[]>([]);
const favorites = ref<any[]>([]);
const ratings = reactive<Record<string, number>>({});
const comments = reactive<Record<string, string>>({});
const restaurantZoom = 13;
const restaurantRefs = new Map<string, HTMLElement>();
const restaurantLocations = reactive<Record<string, { lat: number; lng: number }>>({});
const isAdmin = computed(() => currentUser.value?.role === "ADMIN");

const userLocation = reactive({
  lat: 0,
  lng: 0,
  source: "" // "gps" ou "profile"
});

const geolocating = ref(false);

const loadUserPresence = async () => {
  try {
    const presence = await apiFetch("/presence/me");
    if (presence && presence.latitude && presence.longitude) {
      userLocation.lat = presence.latitude;
      userLocation.lng = presence.longitude;
      userLocation.source = "profile";
    }
  } catch (err) {
    console.warn("Pas de présence sauvegardée");
  }
};

const getLocation = () => {
  return new Promise<void>((resolve) => {
    if (process.client && navigator.geolocation) {
      geolocating.value = true;
      navigator.geolocation.getCurrentPosition(
        (position) => {
          userLocation.lat = position.coords.latitude;
          userLocation.lng = position.coords.longitude;
          userLocation.source = "gps";
          geolocating.value = false;
          resolve();
        },
        (error) => {
          console.error("Erreur géolocalisation:", error);
          geolocating.value = false;
          // Si erreur GPS, on garde la présence sauvegardée si elle existe
          resolve();
        },
        { timeout: 5000, enableHighAccuracy: true }
      );
    } else {
      resolve();
    }
  });
};

const apiFetch = async (path: string, options: any = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  return $fetch(`${config.public.apiBase}${path}`, { ...options, headers });
};

// ... extractLatLng reste identique ...

const loadCurrentUser = async () => {
  try {
    currentUser.value = await apiFetch("/me");
  } catch (err) {
    currentUser.value = null;
  }
};

const searchPlaces = async () => {
  searchMessage.value = null;
  
  // Si pas de localisation du tout, on essaie le GPS en dernier recours
  if (!userLocation.lat || !userLocation.lng) {
    await getLocation();
  }

  try {
    let url = `/restaurants/search?query=${encodeURIComponent(searchQuery.value)}`;
    if (userLocation.lat && userLocation.lng) {
      url += `&latitude=${userLocation.lat}&longitude=${userLocation.lng}`;
    }
    const data: any = await apiFetch(url);
    searchResults.value = data.results || [];
    searchMessage.value = data.message || null;
  } catch (err: any) {
    searchMessage.value = err?.data?.detail || "Erreur search";
  }
};

const loadRestaurants = async (skip = 0, limit = 20) => {
  try {
    const data = await apiFetch(`/restaurants?skip=${skip}&limit=${limit}`);
    restaurants.value = data.items || [];
  } catch (err: any) {
    console.error("Erreur chargement restaurants:", err);
  }
};

const addRestaurant = async (result: any) => {
  try {
    // 1. Créer le restaurant dans la base avec adresse et coordonnées
    await apiFetch("/restaurants", {
      method: "POST",
      body: {
        place_id: result.place_id,
        name: result.name,
        address: result.address,
        latitude: result.lat,
        longitude: result.lng,
        cuisine_tags: null,
        is_official_habit: false
      }
    });
    
    // 2. L'ajouter automatiquement aux favoris
    await apiFetch(`/restaurants/${result.place_id}/favorite`, { method: "POST" });
    
    // 3. Rafraîchir les listes
    await loadFavorites();
    await loadRestaurants();
    
    alert(`"${result.name}" ajouté à vos favoris !`);
  } catch (err: any) {
    console.error("Erreur ajout restaurant:", err);
    // Si erreur 409 (déjà existe), on tente quand même d'ajouter aux favoris
    if (err?.data?.detail?.includes("already")) {
      try {
        await apiFetch(`/restaurants/${result.place_id}/favorite`, { method: "POST" });
        await loadFavorites();
        alert(`"${result.name}" ajouté à vos favoris !`);
      } catch (favErr) {
        alert("Ce restaurant est déjà dans vos favoris");
      }
    } else {
      alert("Erreur lors de l'ajout: " + (err?.data?.detail || err.message));
    }
  }
};

const loadFavorites = async () => {
  try {
    favorites.value = await apiFetch("/me/favorites");
  } catch (err: any) {
    console.error("Erreur chargement favoris:", err);
  }
};

const isFavorite = (placeId: string) => {
  return favorites.value.some((favorite) => favorite.restaurant.place_id === placeId);
};

const toggleFavorite = async (placeId: string) => {
  try {
    if (isFavorite(placeId)) {
      await apiFetch(`/restaurants/${placeId}/favorite`, { method: "DELETE" });
    } else {
      await apiFetch(`/restaurants/${placeId}/favorite`, { method: "POST" });
    }
    loadFavorites();
  } catch (err: any) {
    console.error("Erreur favoris:", err);
  }
};

const extractLatLng = (item: any) => {
  if (!item) return null;
  if (typeof item.latitude === "number" && typeof item.longitude === "number") {
    return { lat: item.latitude, lng: item.longitude };
  }
  if (typeof item.lat === "number" && typeof item.lng === "number") {
    return { lat: item.lat, lng: item.lng };
  }
  if (item.location && typeof item.location.lat === "number" && typeof item.location.lng === "number") {
    return { lat: item.location.lat, lng: item.location.lng };
  }
  if (item.geometry?.location) {
    const { lat, lng } = item.geometry.location;
    if (typeof lat === "number" && typeof lng === "number") {
      return { lat, lng };
    }
  }
  return null;
};

const addRecommendation = async (placeId: string) => {
  try {
    const rating = ratings[placeId];
    const comment = comments[placeId];
    if (!rating) {
      alert("Veuillez sélectionner une note");
      return;
    }
    await apiFetch(`/restaurants/${placeId}/recommendations`, {
      method: "POST",
      body: { rating, comment }
    });
    alert("Avis ajouté !");
    await loadRestaurants();
  } catch (err: any) {
    console.error("Erreur ajout avis:", err);
    alert("Erreur: " + (err?.data?.detail || err.message));
  }
};

const deleteRestaurant = async (placeId: string, name: string) => {
  if (!isAdmin.value) return;
  if (!confirm(`Supprimer le restaurant interne "${name}" ?`)) return;
  try {
    await apiFetch(`/restaurants/${placeId}`, { method: "DELETE" });
    await loadRestaurants();
    await loadFavorites();
  } catch (err: any) {
    console.error("Erreur suppression restaurant:", err);
    alert("Erreur: " + (err?.data?.detail || err.message));
  }
};

const tagList = (tags: string | null): string[] => {
  if (!tags) return [];
  return tags.split(",").map(t => t.trim()).filter(Boolean);
};

const setRestaurantRef = (placeId: string) => (el: HTMLElement | null) => {
  if (el) restaurantRefs.set(placeId, el);
};

const handleRestaurantMarkerClick = (marker: any) => {
  const el = restaurantRefs.get(marker.id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.border = "2px solid var(--accent)";
    setTimeout(() => { el.style.border = ""; }, 2000);
  }
};

const restaurantMarkers = computed(() => {
  const markers: any[] = [];
  
  // Ajouter la position utilisateur comme marqueur (point de départ)
  if (userLocation.lat && userLocation.lng) {
    markers.push({
      id: "user-position",
      lat: userLocation.lat,
      lng: userLocation.lng,
      type: "self",
      popupTitle: "Votre position",
      popupLines: [userLocation.source === "gps" ? "Position GPS" : "Position enregistrée"]
    });
  }
  
  // Restaurants internes
  restaurants.value.forEach((restaurant) => {
    const coords = extractLatLng(restaurant) || restaurantLocations[restaurant.place_id];
    if (!coords) return;
    markers.push({
      id: restaurant.place_id,
      lat: coords.lat,
      lng: coords.lng,
      type: "restaurant",
      popupTitle: restaurant.name,
      popupLines: [
        `Note: ${restaurant.average_rating}`,
        `Avis: ${restaurant.vote_count}`
      ]
    });
  });

  // Résultats de recherche
  searchResults.value.forEach((result) => {
    const coords = extractLatLng(result);
    if (!coords) return;
    const already = markers.find((marker) => marker.id === result.place_id);
    if (already) return;
    markers.push({
      id: result.place_id,
      lat: coords.lat,
      lng: coords.lng,
      type: "restaurant",
      popupTitle: result.name,
      popupLines: [
        result.rating ? `Note: ${result.rating}` : "Note: -",
        result.address ? `Adresse: ${result.address}` : "Adresse: -"
      ]
    });
  });

  return markers;
});

const internalRestaurants = computed(() => {
  return restaurants.value.filter((restaurant) => restaurant.is_official_habit);
});

const restaurantCenter = computed<[number, number]>(() => {
  // Centrer sur la position utilisateur si disponible
  if (userLocation.lat && userLocation.lng) {
    return [userLocation.lat, userLocation.lng];
  }
  const first = restaurantMarkers.value[0];
  if (first) return [first.lat, first.lng];
  return [48.8566, 2.3522];
});

// ...

onMounted(async () => {
  // D'abord on charge la présence sauvegardée (plus rapide et fiable si GPS bloqué)
  await loadUserPresence();
  await loadCurrentUser();
  // Ensuite on essaie d'affiner avec le GPS si possible/autorisé
  getLocation();
  loadRestaurants();
  loadFavorites();
});
</script>
