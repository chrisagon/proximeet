<template>
  <div class="test-page">
    <h1>📅 Test API - Invitations</h1>
    
    <div class="user-info" v-if="user">
      <strong>👤 Connecté:</strong> {{ user.first_name || user.name || user.email }}
    </div>
    
    <div class="status-box">
      <strong>Status:</strong> {{ status }}
    </div>
    
    <div v-if="error" class="error-box">
      ❌ {{ error }}
    </div>
    
    <div v-if="data" class="result-box">
      <h2>Résultat API ({{ data.length }} invitations):</h2>
      <pre>{{ JSON.stringify(data.slice(0, 5), null, 2) }}</pre>
    </div>
    
    <button @click="fetchData" class="refresh-btn" :disabled="loading">
      🔄 Rafraîchir
    </button>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();

const status = ref('Initialisation...');
const error = ref<string | null>(null);
const data = ref<any[] | null>(null);
const user = ref<any>(null);
const loading = ref(false);

// Récupérer les infos utilisateur comme sur le Dashboard
const fetchUser = async () => {
  try {
    await handleRedirect();
    const accessToken = token.value || (await acquireToken());
    if (!accessToken) {
      status.value = 'Non connecté - Veuillez vous authentifier';
      return;
    }
    
    const userData = await $fetch(`${config.public.apiBase}/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      }
    });
    user.value = userData;
  } catch (err: any) {
    console.error('Erreur récupération user:', err);
  }
};

const fetchData = async () => {
  status.value = 'Chargement...';
  error.value = null;
  loading.value = true;
  
  try {
    await handleRedirect();
    const accessToken = token.value || (await acquireToken());
    
    if (!accessToken) {
      error.value = 'Non authentifié - Veuillez vous connecter via Microsoft';
      status.value = 'Erreur auth';
      return;
    }
    
    // Ajouter un timestamp pour éviter le cache
    const timestamp = Date.now();
    const result = await $fetch(`${config.public.apiBase}/invitations/received?_t=${timestamp}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
      }
    });
    
    data.value = result;
    status.value = `OK - ${result.length} invitations chargées`;
    
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement';
    status.value = 'Erreur';
    console.error('Erreur API:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchUser();
  await fetchData();
});
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.user-info {
  margin: 10px 0;
  padding: 10px;
  background: #e8f5e9;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
}

.status-box {
  margin: 20px 0;
  padding: 15px;
  background: #f0f0f0;
  border-radius: 8px;
}

.error-box {
  color: red;
  margin: 20px 0;
  padding: 15px;
  background: #ffebee;
  border-radius: 8px;
}

.result-box {
  margin: 20px 0;
}

.result-box pre {
  background: #1e293b;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.refresh-btn {
  margin-top: 20px;
  padding: 12px 24px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.refresh-btn:hover:not(:disabled) {
  background: #357abd;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
