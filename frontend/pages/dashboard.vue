<template>
  <section class="section">
    <div class="card" v-if="user">
      <h1 style="margin:0; font-size:1.5rem;">Bonjour {{ user.first_name || user.nickname || 'consultant' }} 👋</h1>
      <p class="mono" style="margin:0.5rem 0 0 0; color:var(--sea);">Prêt à déjeuner avec vos collègues ?</p>
    </div>

    <!-- Invitations et Notifications -->
    <div class="card" v-if="invitations.length > 0 || notifications.length > 0 || acceptedInvitations.length > 0">
      <h2 class="section-title">🔔 Invitations et notifications</h2>
      
      <!-- Lien vers le calendrier -->
      <div v-if="acceptedInvitations.length > 0" style="margin-bottom: 1.5rem;">
        <NuxtLink to="/calendar" class="btn" style="display: inline-flex; align-items: center; gap: 0.5rem;">
          📅 Voir mon agenda ({{ acceptedInvitations.length }} rendez-vous)
        </NuxtLink>
      </div>
      
      <!-- Invitations en attente -->
      <div v-if="invitations.length > 0" style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 1rem; margin-bottom: 0.8rem; color: var(--accent);">Invitations à répondre</h3>
        <div class="card-grid">
          <div class="card" v-for="invitation in pendingInvitations" :key="invitation.id" style="border-left: 3px solid var(--accent);">
            <strong>📨 Nouvelle invitation</strong>
            <p class="mono" style="margin-top: 0.5rem; line-height: 1.5;">
              <strong>{{ invitation.organizer_name || 'Quelqu\'un' }}</strong> vous invite au restaurant
              <strong>"{{ invitation.restaurant_name || 'un restaurant' }}"</strong>
            </p>
            <p class="mono" style="margin-top: 0.3rem; padding: 0.4rem 0.6rem; background: #fff7ed; border-radius: 6px; display: inline-block;">
              <template v-if="invitation.scheduled_at">
                📅 <strong style="color: var(--accent);">{{ new Date(invitation.scheduled_at).toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</strong>
                à <strong style="color: var(--accent);">{{ new Date(invitation.scheduled_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) }}</strong>
              </template>
              <template v-else>
                📅 <em style="color: #666;">Date à préciser</em>
              </template>
            </p>
            <p class="mono" v-if="invitation.message" style="margin-top: 0.5rem; font-style: italic; color: #666;">
              💬 "{{ invitation.message }}"
            </p>
            <div style="display:flex; gap:0.5rem; margin-top:0.8rem;">
              <button class="btn" @click="respondToInvitation(invitation.id, 'ACCEPTED')" :disabled="responding[invitation.id]">
                ✅ Accepter
              </button>
              <button class="btn secondary" @click="respondToInvitation(invitation.id, 'DECLINED')" :disabled="responding[invitation.id]">
                ❌ Refuser
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Autres notifications -->
      <div v-if="notifications.length > 0" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
          <h3 style="font-size: 1rem; margin: 0; color: var(--sea);">Notifications</h3>
          <button 
            v-if="readNotifications.length > 0"
            class="btn mini danger" 
            @click="deleteAllReadNotifications"
          >
            🗑️ Tout supprimer
          </button>
        </div>
        <div class="card-grid">
          <div class="card" v-for="notif in notifications" :key="notif.id" :class="{ 'notification-unread': !notif.is_read }" style="background: #f8fafc;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <strong>{{ notif.title }}</strong>
              <button class="btn mini danger" @click="deleteNotification(notif.id)">🗑️</button>
            </div>
            <p class="mono">{{ notif.message }}</p>
            <button 
              v-if="!notif.is_read" 
              class="btn mini secondary" 
              @click="markNotificationRead(notif.id)" 
              style="margin-top: 0.5rem;"
            >
              Marquer comme lue
            </button>
          </div>
        </div>
      </div>

      <!-- Invitations déclinées -->
      <div v-if="declinedInvitations.length > 0" style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 1rem; margin-bottom: 0.8rem; color: #dc2626;">Invitations déclinées</h3>
        <div class="card-grid">
          <div class="card" v-for="invitation in declinedInvitations" :key="invitation.id" style="border-left: 3px solid #dc2626; opacity: 0.8;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <strong>❌ Invitation déclinée</strong>
              <button class="btn mini danger" @click="clearDeclinedInvitation(invitation.id)">🗑️ Supprimer</button>
            </div>
            <p class="mono" style="margin-top: 0.5rem; line-height: 1.5;">
              <strong>{{ invitation.organizer_name || 'Quelqu\'un' }}</strong> vous invite au restaurant
              <strong>"{{ invitation.restaurant_name || 'un restaurant' }}"</strong>
              <span v-if="invitation.scheduled_at">
                le <strong>{{ new Date(invitation.scheduled_at).toLocaleDateString('fr-FR') }}</strong>
                à <strong>{{ new Date(invitation.scheduled_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) }}</strong>
              </span>
            </p>
          </div>
        </div>
      </div>

      <button class="btn secondary" @click="loadInvitationsAndNotifications" style="margin-top: 1rem;">
        🔄 Rafraîchir
      </button>
    </div>

    <div class="card">
      <h2 class="section-title">Presence</h2>
      <div v-if="geolocating" class="mono" style="color:var(--sea); margin-bottom:1rem;">
        📍 Détection de votre position en cours...
      </div>
      <div v-if="!geolocating && hasCoords(presenceForm.latitude, presenceForm.longitude)" class="mono" style="color:#2f9e44; margin-bottom:1rem;">
        ✓ Position détectée
      </div>
      <div style="display:flex; gap:0.8rem; margin-bottom:1rem;">
        <button class="btn secondary" @click="getLocation" :disabled="geolocating">
          {{ geolocating ? 'Localisation...' : 'Actualiser position' }}
        </button>
      </div>
      <p v-if="geoError" class="mono" style="color:var(--accent);">{{ geoError }}</p>
      <div class="field">
        <label>Latitude</label>
        <input v-model.number="presenceForm.latitude" type="number" step="0.0001" />
      </div>
      <div class="field">
        <label>Longitude</label>
        <input v-model.number="presenceForm.longitude" type="number" step="0.0001" />
      </div>
      <div class="field">
        <label>Type</label>
        <select v-model="presenceForm.location_type">
          <option value="CLIENT">Client</option>
          <option value="HOME">Home</option>
        </select>
      </div>
      <div class="field">
        <label>Expiration (heures)</label>
        <input v-model.number="presenceForm.expires_in_hours" type="number" min="1" />
      </div>
      <div style="display:flex; gap:0.8rem; margin-top:1rem;">
        <button class="btn" @click="sharePresence">Partager presence</button>
        <button class="btn secondary" @click="loadPresence">Actualiser</button>
      </div>
      <p class="mono" v-if="presence">Expire: {{ new Date(presence.expires_at).toLocaleString() }}</p>
      <p v-if="error" class="mono">{{ error }}</p>
    </div>

    <div class="card">
      <h2 class="section-title">Recherche de proximite</h2>
      <div class="field">
        <label>Rayon (km)</label>
        <select v-model.number="radius">
          <option :value="1">1 km</option>
          <option :value="3">3 km</option>
          <option :value="5">5 km</option>
          <option :value="10">10 km</option>
          <option :value="20">20 km</option>
        </select>
      </div>
      <button class="btn" style="margin-top:1rem;" @click="() => loadNearby()">Trouver des collegues</button>
      <div class="card-grid" style="margin-top:1rem;">
        <div class="card" v-for="person in nearby" :key="person.user_id">
          <strong>{{ person.first_name || person.nickname || person.user_id }}</strong>
          <p class="mono">{{ person.distance_km }} km</p>
          <p class="mono">{{ person.privacy_level }}</p>
          <button class="btn secondary" @click="openInviteModal(person)">Inviter</button>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="section-title">Carte des presences</h2>
      <ProximeetMap
        :center="mapCenter"
        :zoom="mapZoom"
        :markers="mapMarkers"
        @marker-click="handleMarkerClick"
        @map-click="handleMapClick"
      />
      <p class="mono" style="margin-top:0.8rem;">
        Bleu: vous. Vert: collegues. Halo: mode bubble.
      </p>
    </div>

    <InviteModal
      :open="inviteModalOpen"
      :invitee-name="inviteeDisplayName"
      :favorites="favorites"
      :error="inviteError || ''"
      @close="closeInviteModal"
      @send="sendInvitation"
    />
  </section>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();
const user = ref<any>(null);
const presence = ref<any>(null);
const nearby = ref<any[]>([]);
const error = ref<string | null>(null);
const radius = ref(1);
const mapZoom = 13;
const bubbleRadiusMeters = 300;
const favorites = ref<any[]>([]);
const inviteModalOpen = ref(false);
const invitee = ref<any>(null);
const inviteError = ref<string | null>(null);
const presenceForm = reactive({
  latitude: 0,
  longitude: 0,
  location_type: "CLIENT",
  expires_in_hours: 6
});

const geolocating = ref(false);
const geoError = ref<string | null>(null);

// Storage key for position persistence
const POSITION_STORAGE_KEY = 'proximeet_position';
const POSITION_MAX_AGE_MS = 30 * 60 * 1000; // 30 minutes

interface StoredPosition {
  lat: number;
  lng: number;
  timestamp: number;
}

const hasValidStoredPosition = (): boolean => {
  if (!process.client) return false;
  
  // Check if presenceForm already has valid coordinates
  if (hasCoords(presenceForm.latitude, presenceForm.longitude)) {
    return true;
  }
  
  // Check localStorage for valid stored position
  try {
    const stored = localStorage.getItem(POSITION_STORAGE_KEY);
    if (stored) {
      const pos: StoredPosition = JSON.parse(stored);
      const age = Date.now() - pos.timestamp;
      if (age < POSITION_MAX_AGE_MS && hasCoords(pos.lat, pos.lng)) {
        // Restore to presenceForm
        presenceForm.latitude = pos.lat;
        presenceForm.longitude = pos.lng;
        return true;
      }
    }
  } catch (e) {
    console.warn('Error reading stored position:', e);
  }
  
  return false;
};

const storePosition = (lat: number, lng: number) => {
  if (!process.client) return;
  try {
    localStorage.setItem(POSITION_STORAGE_KEY, JSON.stringify({
      lat,
      lng,
      timestamp: Date.now()
    }));
  } catch (e) {
    console.warn('Error storing position:', e);
  }
};

const getLocation = () => {
  // CRITIQUE : Vérifier qu'on est côté client
  if (!process.client) {
    geoError.value = "Géolocalisation disponible uniquement côté client";
    return;
  }
  
  geolocating.value = true;
  geoError.value = null;
  
  if (!navigator.geolocation) {
    geoError.value = "Géolocalisation non supportée par votre navigateur";
    geolocating.value = false;
    return;
  }
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      presenceForm.latitude = position.coords.latitude;
      presenceForm.longitude = position.coords.longitude;
      // Store position for persistence
      storePosition(position.coords.latitude, position.coords.longitude);
      geolocating.value = false;
      
      // Proposer de partager automatiquement
      if (confirm("Position détectée ! Voulez-vous la partager maintenant ?")) {
        sharePresence();
      }
    },
    (error) => {
      geoError.value = `Erreur géolocalisation: ${error.message}`;
      geolocating.value = false;
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
  );
};

const hasCoords = (lat?: number | null, lng?: number | null) => {
  if (typeof lat !== "number" || typeof lng !== "number") return false;
  return !(lat === 0 && lng === 0);
};

const mapCenter = computed<[number, number]>(() => {
  if (hasCoords(presenceForm.latitude, presenceForm.longitude)) {
    return [presenceForm.latitude, presenceForm.longitude];
  }
  if (presence.value && hasCoords(presence.value.latitude, presence.value.longitude)) {
    return [presence.value.latitude, presence.value.longitude];
  }
  const nearbyWithCoords = nearby.value.find((person) => hasCoords(person.latitude, person.longitude));
  if (nearbyWithCoords) {
    return [nearbyWithCoords.latitude, nearbyWithCoords.longitude];
  }
  return [48.8566, 2.3522];
});

const mapMarkers = computed(() => {
  const markers: any[] = [];
  if (hasCoords(presenceForm.latitude, presenceForm.longitude)) {
    markers.push({
      id: "self",
      lat: presenceForm.latitude,
      lng: presenceForm.longitude,
      type: "self",
      popupTitle: "Votre position",
      popupLines: [presenceForm.location_type]
    });
  } else if (presence.value && hasCoords(presence.value.latitude, presence.value.longitude)) {
    markers.push({
      id: "self",
      lat: presence.value.latitude,
      lng: presence.value.longitude,
      type: "self",
      popupTitle: "Votre position",
      popupLines: [presence.value.location_type]
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
      popupLines: [
        `${person.distance_km} km`,
        person.privacy_level
      ],
      bubbleRadiusMeters: person.privacy_level === "BUBBLE" ? bubbleRadiusMeters : 0
    });
  });

  return markers;
});

const handleMarkerClick = (marker: any) => {
  if (marker?.id === "self") return;
};

const handleMapClick = (latlng: { lat: number; lng: number }) => {
  if (!latlng) return;
};

const apiFetch = async (path: string, options: any = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return $fetch(`${config.public.apiBase}${path}`, {
    ...options,
    headers
  });
};

const inviteeDisplayName = computed(() => {
  if (!invitee.value) return "";
  return invitee.value.first_name || invitee.value.nickname || invitee.value.user_id || "";
});

const loadFavorites = async () => {
  try {
    favorites.value = await apiFetch("/me/favorites");
  } catch (err: any) {
    console.error("Erreur chargement favoris:", err);
  }
};

const openInviteModal = async (person: any) => {
  invitee.value = person;
  inviteError.value = null;
  inviteModalOpen.value = true;
  await loadFavorites();
};

const closeInviteModal = () => {
  inviteModalOpen.value = false;
};

const sendInvitation = async (payload: { restaurant_id: string; message: string; scheduled_at: string }) => {
  if (!invitee.value) return;
  inviteError.value = null;
  try {
    await apiFetch("/invitations", {
      method: "POST",
      body: {
        invitee_id: invitee.value.user_id,
        restaurant_id: payload.restaurant_id,
        message: payload.message,
        scheduled_at: payload.scheduled_at
      }
    });
    inviteModalOpen.value = false;
  } catch (err: any) {
    inviteError.value = err?.data?.detail || "Erreur invitation";
  }
};

const sharePresence = async () => {
  error.value = null;
  try {
    presence.value = await apiFetch("/presence", {
      method: "POST",
      body: presenceForm
    });
  } catch (err: any) {
    error.value = err?.data?.detail || "Erreur presence";
  }
};

const loadPresence = async () => {
  error.value = null;
  try {
    presence.value = await apiFetch("/presence/me");
    // Fix: Populate presenceForm with last presence data or fallback to Paris
    if (presence.value) {
      presenceForm.latitude = presence.value.latitude || 48.86604857230349;
      presenceForm.longitude = presence.value.longitude || 2.336806929087687;
      // Store valid server position in localStorage
      if (hasCoords(presence.value.latitude, presence.value.longitude)) {
        storePosition(presence.value.latitude, presence.value.longitude);
      }
    } else {
      // Fallback: Paris coordinates for anonymous/logged user without presence
      presenceForm.latitude = 48.86604857230349;
      presenceForm.longitude = 2.336806929087687;
    }
  } catch (err: any) {
    error.value = err?.data?.detail || "Erreur presence";
  }
};

const loadNearby = async (skip = 0, limit = 20) => {
  error.value = null;
  try {
    const data = await apiFetch(`/nearby?radius_km=${radius.value}&skip=${skip}&limit=${limit}`);
    nearby.value = data.items || [];
  } catch (err: any) {
    error.value = err?.data?.detail || "Erreur proximite";
  }
};

const loadUser = async () => {
  try {
    user.value = await apiFetch("/me");
  } catch (err: any) {
    console.error("Erreur chargement utilisateur:", err);
  }
};

// Invitations et notifications
const invitations = ref<any[]>([]);
const acceptedMeetings = ref<any[]>([]);
const notifications = ref<any[]>([]);
const responding = ref<Record<string, boolean>>({});

const pendingInvitations = computed(() => 
  invitations.value.filter(inv => inv.status === 'PENDING')
);

const declinedInvitations = computed(() => 
  invitations.value.filter(inv => inv.status === 'DECLINED')
);

const acceptedInvitations = computed(() => acceptedMeetings.value);

const unreadNotifications = computed(() => 
  notifications.value.filter(notif => !notif.is_read && notif.type !== 'invitation_received')
);

const readNotifications = computed(() => 
  notifications.value.filter(notif => notif.is_read)
);

const getInvitationMessage = (invitation: any) => {
  const organizer = invitation.organizer_name || 'Quelqu\'un';
  const restaurant = invitation.restaurant_name || 'un restaurant';
  const message = invitation.message || '';
  
  let text = `${organizer} vous invite au restaurant "${restaurant}"`;
  
  if (invitation.scheduled_at) {
    const date = new Date(invitation.scheduled_at);
    const dateStr = date.toLocaleDateString('fr-FR');
    const timeStr = date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    text += ` le ${dateStr} à ${timeStr}`;
  }
  
  if (message) {
    text += `. ${message}`;
  }
  
  return text;
};

const loadInvitations = async () => {
  try {
    invitations.value = await apiFetch("/invitations/received");
  } catch (err: any) {
    console.error("Erreur chargement invitations:", err);
  }
};

const loadAcceptedMeetings = async () => {
  try {
    // Bilateral meetings (organizer + invitee) for agenda counter
    acceptedMeetings.value = await apiFetch("/invitations/accepted-meetings");
  } catch (err: any) {
    console.error("Erreur chargement invitations:", err);
  }
};

const loadNotifications = async () => {
  try {
    notifications.value = await apiFetch("/notifications");
  } catch (err: any) {
    console.error("Erreur chargement notifications:", err);
  }
};

const loadInvitationsAndNotifications = async () => {
  await Promise.all([loadInvitations(), loadAcceptedMeetings(), loadNotifications()]);
};

const respondToInvitation = async (invitationId: number, status: 'ACCEPTED' | 'DECLINED') => {
  responding.value[invitationId] = true;
  try {
    await apiFetch(`/invitations/${invitationId}`, {
      method: "PATCH",
      body: { status }
    });
    await loadInvitations();
    await loadAcceptedMeetings();
    await loadNotifications();
    alert(status === 'ACCEPTED' ? 'Invitation acceptée !' : 'Invitation refusée.');
  } catch (err: any) {
    console.error("Erreur réponse invitation:", err);
    alert(err?.data?.detail || "Erreur lors de la réponse");
  } finally {
    responding.value[invitationId] = false;
  }
};

const markNotificationRead = async (notificationId: number) => {
  try {
    await apiFetch(`/notifications/${notificationId}/read`, {
      method: "PATCH"
    });
    await loadNotifications();
  } catch (err: any) {
    console.error("Erreur marquer notification lue:", err);
  }
};

const deleteNotification = async (notificationId: number) => {
  if (!confirm('Supprimer cette notification ?')) return;
  try {
    await apiFetch(`/notifications/${notificationId}`, {
      method: "DELETE"
    });
    await loadNotifications();
  } catch (err: any) {
    console.error("Erreur suppression notification:", err);
    alert(err?.data?.detail || "Erreur lors de la suppression");
  }
};

const deleteAllReadNotifications = async () => {
  if (!confirm('Supprimer toutes les notifications lues ?')) return;
  try {
    await apiFetch("/notifications", {
      method: "DELETE"
    });
    await loadNotifications();
  } catch (err: any) {
    console.error("Erreur suppression notifications:", err);
    alert(err?.data?.detail || "Erreur lors de la suppression");
  }
};

const clearDeclinedInvitation = async (invitationId: number) => {
  if (!confirm('Supprimer cette invitation déclinée de votre liste ?')) return;
  try {
    await apiFetch(`/invitations/${invitationId}/clear`, {
      method: "DELETE"
    });
    await loadInvitations();
  } catch (err: any) {
    console.error("Erreur suppression invitation:", err);
    alert(err?.data?.detail || "Erreur lors de la suppression");
  }
};

// Géolocalisation automatique au chargement de la page
onMounted(async () => {
  // S'assurer qu'on est bien côté client
  if (process.client) {
    // Charger les infos utilisateur
    await loadUser();
    
    // Charger la présence existante si disponible
    await loadPresence();
    
    // Ne lancer la géoloc auto QUE si pas de position valide existante
    // La position peut venir de: localStorage, presenceForm (restauré), ou presence (serveur)
    if (!hasValidStoredPosition()) {
      getLocation();
    }
    
    // Charger invitations et notifications
    await loadInvitationsAndNotifications();
  }
});
</script>
