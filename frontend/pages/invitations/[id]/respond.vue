<template>
  <div class="page">
    <div class="card" style="max-width: 480px; margin: 2rem auto; text-align: center;">
      <div v-if="loading">
        <h2>Traitement en cours...</h2>
        <p class="mono">Veuillez patienter</p>
      </div>
      
      <div v-else-if="needsAction">
        <h2>Répondre à l'invitation</h2>
        <p class="mono">Choisissez une action</p>
        <div style="display: flex; gap: 0.6rem; justify-content: center; margin-top: 1rem;">
          <button class="btn" @click="respondWithAuth('ACCEPTED')">
            ✅ Accepter
          </button>
          <button class="btn secondary" @click="respondWithAuth('DECLINED')">
            ❌ Refuser
          </button>
        </div>
      </div>
      
      <div v-else-if="success">
        <div style="font-size: 4rem; margin-bottom: 1rem;">
          {{ action === 'accept' ? '✅' : '❌' }}
        </div>
        <h2>{{ action === 'accept' ? 'Invitation acceptée !' : 'Invitation refusée' }}</h2>
        <p class="mono">{{ message }}</p>
        <NuxtLink to="/" class="btn" style="margin-top: 1rem;">
          Aller sur Proximeet
        </NuxtLink>
      </div>
      
      <div v-else>
        <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
        <h2>Erreur</h2>
        <p class="mono" style="color: var(--accent);">{{ error }}</p>
        <NuxtLink to="/" class="btn" style="margin-top: 1rem;">
          Aller sur Proximeet
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const route = useRoute();
const { token, acquireToken, handleRedirect } = useAuth();

const loading = ref(true);
const success = ref(false);
const needsAction = ref(false);
const error = ref("");
const message = ref("");
const action = ref("");

const invitationId = route.params.id;
const actionParam = route.query.action as string;
const invitationToken = route.query.token as string;

const apiFetch = async (path: string, options: any = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  return $fetch(`${config.public.apiBase}${path}`, { ...options, headers });
};

const respondWithAuth = async (status: 'ACCEPTED' | 'DECLINED') => {
  loading.value = true;
  error.value = "";
  try {
    await apiFetch(`/invitations/${invitationId}`, {
      method: "PATCH",
      body: { status }
    });
    action.value = status === 'ACCEPTED' ? 'accept' : 'decline';
    success.value = true;
    needsAction.value = false;
    message.value = status === 'ACCEPTED'
      ? "Invitation acceptée avec succès"
      : "Invitation refusée avec succès";
  } catch (err: any) {
    success.value = false;
    error.value = err?.data?.detail || "Une erreur est survenue lors du traitement de l'invitation";
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  action.value = actionParam;
  
  if (!invitationId) {
    error.value = "Lien invalide - paramètres manquants";
    loading.value = false;
    return;
  }
  
  if (actionParam && invitationToken) {
    if (actionParam !== 'accept' && actionParam !== 'decline') {
      error.value = "Action non reconnue";
      loading.value = false;
      return;
    }
    
    try {
      const result = await $fetch(`${config.public.apiBase}/invitations/${invitationId}/respond`, {
        method: "POST",
        params: { action: actionParam, token: invitationToken }
      });
      
      success.value = true;
      message.value = result.message;
    } catch (err: any) {
      success.value = false;
      error.value = err?.data?.detail || "Une erreur est survenue lors du traitement de l'invitation";
    } finally {
      loading.value = false;
    }
  } else {
    needsAction.value = true;
    loading.value = false;
  }
});
</script>
