<template>
  <div class="page">
    <div class="card">
      <h1>📨 Mes Invitations</h1>
      <p class="mono">Gérez vos invitations reçues</p>
      
      <div v-if="loading" class="mono">Chargement...</div>
      
      <div v-else-if="invitations.length === 0" class="mono">
        Aucune invitation pour le moment.
      </div>
      
      <div v-else class="invitations-list">
        <div 
          v-for="invitation in invitations" 
          :key="invitation.id"
          class="invitation-card"
          :class="{ 'pending': invitation.status === 'PENDING', 'accepted': invitation.status === 'ACCEPTED', 'declined': invitation.status === 'DECLINED' }"
        >
          <div class="invitation-header">
            <h3>{{ invitation.restaurant_name }}</h3>
            <span class="status-badge" :class="invitation.status">
              {{ formatStatus(invitation.status) }}
            </span>
          </div>
          
          <p class="invitation-details">
            <strong>De:</strong> {{ invitation.organizer_name }}
          </p>
          
          <p v-if="invitation.scheduled_at" class="invitation-details">
            <strong>📅 Date:</strong> {{ formatDate(invitation.scheduled_at) }}
          </p>
          
          <p v-if="invitation.message" class="invitation-message">
            "{{ invitation.message }}"
          </p>
          
          <!-- Boutons d'action pour les invitations PENDING -->
          <div v-if="invitation.status === 'PENDING'" class="invitation-actions">
            <button 
              class="btn success" 
              @click="respondToInvitation(invitation, 'ACCEPTED')"
              :disabled="responding[invitation.id]"
            >
              {{ responding[invitation.id] === 'ACCEPTED' ? '⏳ Acceptation...' : '✅ Accepter' }}
            </button>
            <button 
              class="btn danger" 
              @click="respondToInvitation(invitation, 'DECLINED')"
              :disabled="responding[invitation.id]"
            >
              {{ responding[invitation.id] === 'DECLINED' ? '⏳ Refus...' : '❌ Refuser' }}
            </button>
          </div>
          
          <div v-else class="invitation-status-msg">
            <span v-if="invitation.status === 'ACCEPTED'">✅ Vous avez accepté cette invitation</span>
            <span v-if="invitation.status === 'DECLINED'">❌ Vous avez refusé cette invitation</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();

const invitations = ref<any[]>([]);
const loading = ref(false);
const responding = ref<Record<string, string | null>>({});

const isAuthenticated = computed(() => !!token.value);

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

const formatStatus = (status: string) => {
  const statusMap: Record<string, string> = {
    'PENDING': 'En attente',
    'ACCEPTED': 'Acceptée',
    'DECLINED': 'Refusée'
  };
  return statusMap[status] || status;
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const loadInvitations = async () => {
  if (!isAuthenticated.value) return;
  loading.value = true;
  try {
    invitations.value = await apiFetch("/invitations/received");
  } catch (err) {
    console.error("Erreur chargement invitations:", err);
  } finally {
    loading.value = false;
  }
};

const respondToInvitation = async (invitation: any, status: 'ACCEPTED' | 'DECLINED') => {
  responding.value[invitation.id] = status;
  try {
    await apiFetch(`/invitations/${invitation.id}`, {
      method: "PATCH",
      body: { status }
    });
    
    // Mettre à jour localement
    invitation.status = status;
    
    alert(status === 'ACCEPTED' ? '✅ Invitation acceptée ! Le rendez-vous est ajouté à votre agenda.' : '❌ Invitation refusée.');
  } catch (err: any) {
    console.error("Erreur réponse invitation:", err);
    alert(err?.data?.detail || "Erreur lors de la réponse à l'invitation");
  } finally {
    responding.value[invitation.id] = null;
  }
};

onMounted(() => {
  loadInvitations();
});
</script>

<style scoped>
.invitations-list {
  display: grid;
  gap: 1rem;
  margin-top: 1.5rem;
}

.invitation-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1.2rem;
  border-left: 4px solid #94a3b8;
  transition: all 0.2s;
}

.invitation-card.pending {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.invitation-card.accepted {
  border-left-color: #10b981;
  background: #ecfdf5;
}

.invitation-card.declined {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.invitation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.invitation-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.PENDING {
  background: #f59e0b;
  color: white;
}

.status-badge.ACCEPTED {
  background: #10b981;
  color: white;
}

.status-badge.DECLINED {
  background: #ef4444;
  color: white;
}

.invitation-details {
  margin: 0.4rem 0;
  color: #64748b;
  font-size: 0.9rem;
}

.invitation-message {
  margin: 0.8rem 0;
  padding: 0.8rem;
  background: white;
  border-radius: 8px;
  font-style: italic;
  color: #475569;
}

.invitation-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
}

.invitation-actions .btn {
  flex: 1;
}

.invitation-actions .btn.success {
  background: #10b981;
  color: white;
}

.invitation-actions .btn.success:hover {
  background: #059669;
}

.invitation-actions .btn.danger {
  background: #ef4444;
  color: white;
}

.invitation-actions .btn.danger:hover {
  background: #dc2626;
}

.invitation-status-msg {
  margin-top: 1rem;
  padding: 0.6rem;
  background: white;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}
</style>