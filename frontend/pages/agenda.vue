<template>
  <section class="section">
    <div class="card">
      <h1 style="margin:0; font-size:1.5rem;">📅 Mon Agenda</h1>
      <p class="mono" style="margin:0.5rem 0 0 0; color:var(--sea);">Vos invitations acceptées</p>
    </div>

    <!-- DEBUG INFO -->
    <div v-if="debugInfo" class="card" style="background: #fef3c7; border: 2px solid #f59e0b;">
      <h3>🔧 Debug Info</h3>
      <pre class="mono" style="font-size: 0.8rem; white-space: pre-wrap;">{{ debugInfo }}</pre>
    </div>

    <!-- Liste simple sans calendrier -->
    <div class="card">
      <h2 class="section-title">📋 Mes invitations acceptées</h2>
      
      <div v-if="loading" class="mono">Chargement...</div>
      <div v-else-if="invitations.length === 0" class="mono">
        Aucune invitation trouvée.
      </div>
      <div v-else>
        <p class="mono" style="margin-bottom: 1rem;">
          Total: {{ invitations.length }} invitations | 
          Acceptées: {{ acceptedCount }} | 
          Sans date: {{ noDateCount }}
        </p>
        
        <div class="card-grid">
          <div 
            v-for="invitation in filteredAcceptedInvitations" 
            :key="invitation.id"
            class="card" 
            :style="{ borderLeft: invitation.scheduled_at ? '3px solid #22c55e' : '3px solid #f59e0b' }"
          >
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <strong>✅ {{ invitation.restaurant_name || 'Restaurant' }}</strong>
              <span class="mono" style="font-size: 0.8rem;" :style="{ color: invitation.scheduled_at ? '#22c55e' : '#f59e0b' }">
                {{ invitation.scheduled_at ? 'Avec date' : 'Sans date' }}
              </span>
            </div>
            <p class="mono" style="margin-top: 0.5rem;">
              📅 {{ invitation.scheduled_at ? formatDate(invitation.scheduled_at) : 'Date non définie' }}
            </p>
            <p class="mono" style="margin-top: 0.3rem;">
              👤 {{ invitation.organizer_name || invitation.organizer_email }}
              <span v-if="invitation.organizer_name && invitation.organizer_name.includes('(invité)')" class="mono" style="font-size: 0.75rem; color: #666;">
                - Vous êtes l'organisateur
              </span>
            </p>
          </div>
        </div>
      </div>
      
      <button class="btn secondary" @click="loadInvitations" style="margin-top: 1rem;">
        🔄 Rafraîchir
      </button>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();

const loading = ref(true);
const invitations = ref([]);
const debugInfo = ref('');

const startOfToday = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
};

const isTodayOrFuture = (dateString) => {
  if (!dateString) return true;
  const date = new Date(dateString);
  return date.getTime() >= startOfToday().getTime();
};

const filteredAcceptedInvitations = computed(() =>
  invitations.value.filter(i => i.status === 'ACCEPTED' && isTodayOrFuture(i.scheduled_at))
);

const acceptedCount = computed(() => filteredAcceptedInvitations.value.length);
const noDateCount = computed(() =>
  filteredAcceptedInvitations.value.filter(i => i.status === 'ACCEPTED' && !i.scheduled_at).length
);

const apiFetch = async (path, options = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return $fetch(`${config.public.apiBase}${path}`, { ...options, headers });
};

const loadInvitations = async () => {
  loading.value = true;
  debugInfo.value = 'Chargement...';
  try {
    // Utiliser le nouvel endpoint pour récupérer toutes les invitations acceptées
    // (en tant qu'invité ET en tant qu'organisateur)
    const data = await apiFetch("/invitations/accepted-meetings");
    invitations.value = data;
    debugInfo.value = JSON.stringify({
      total: data.length,
      sample: data.slice(0, 2).map(i => ({ 
        id: i.id, 
        status: i.status, 
        scheduled_at: i.scheduled_at,
        restaurant: i.restaurant_name 
      }))
    }, null, 2);
  } catch (err) {
    debugInfo.value = 'Erreur: ' + err.message;
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'Date non définie';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(() => {
  loadInvitations();
});
</script>
