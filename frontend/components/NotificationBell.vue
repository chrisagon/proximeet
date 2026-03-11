<template>
  <div class="notification-bell" v-if="isAuthenticated">
    <button class="btn secondary" @click="togglePanel">
      🔔 Notifications
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>
    <div v-if="open" class="notification-panel">
      <div class="notification-header">
        <strong>Notifications</strong>
        <button class="btn mini" @click="refresh">Rafraichir</button>
      </div>
      <div v-if="loading" class="mono">Chargement...</div>
      <div v-else-if="notifications.length === 0" class="mono">Aucune notification.</div>
      <ul v-else class="notification-list">
        <li v-for="notification in notifications" :key="notification.id" :class="{ 'invitation-item': notification.type === 'invitation_received' }">
          <div class="notification-title">
            <strong>{{ notification.title }}</strong>
            <div class="notification-actions">
              <button
                v-if="!notification.is_read"
                class="btn mini"
                @click="markAsRead(notification.id)"
              >
                Marquer lue
              </button>
              <button
                class="btn mini danger"
                @click="deleteNotification(notification.id)"
                title="Supprimer"
              >
                🗑️
              </button>
            </div>
          </div>
          <p class="mono">{{ notification.message }}</p>
          
          <!-- Boutons d'action pour les invitations PENDING -->
          <div v-if="notification.type === 'invitation_received' && invitationStatuses[notification.data] === 'PENDING'" class="invitation-actions">
            <button 
              class="btn mini success" 
              @click="respondToInvitation(notification, 'ACCEPTED')"
              :disabled="responding[notification.data]"
            >
              {{ responding[notification.data] === 'ACCEPTED' ? '...' : '✅ Accepter' }}
            </button>
            <button 
              class="btn mini danger" 
              @click="respondToInvitation(notification, 'DECLINED')"
              :disabled="responding[notification.data]"
            >
              {{ responding[notification.data] === 'DECLINED' ? '...' : '❌ Refuser' }}
            </button>
          </div>
          <!-- Message de statut si déjà traitée -->
          <div v-else-if="notification.type === 'invitation_received' && invitationStatuses[notification.data]" class="invitation-status">
            <span v-if="invitationStatuses[notification.data] === 'ACCEPTED'" class="status-accepted">✅ Acceptée</span>
            <span v-if="invitationStatuses[notification.data] === 'DECLINED'" class="status-declined">❌ Refusée</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();

const notifications = ref<any[]>([]);
const loading = ref(false);
const open = ref(false);
const responding = ref<Record<string, string | null>>({});
const invitationStatuses = ref<Record<string, string>>({});

const isAuthenticated = computed(() => !!token.value);
const unreadCount = computed(() => notifications.value.filter((item) => !item.is_read).length);

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

const refresh = async () => {
  if (!isAuthenticated.value) return;
  loading.value = true;
  try {
    notifications.value = await apiFetch("/notifications");
    // Charger les statuts des invitations pour les notifications d'invitation
    for (const notification of notifications.value) {
      if (notification.type === 'invitation_received' && notification.data) {
        try {
          const invitation = await apiFetch(`/invitations/${notification.data}`);
          invitationStatuses.value[notification.data] = invitation.status;
        } catch (err) {
          console.error(`Erreur chargement invitation ${notification.data}:`, err);
        }
      }
    }
  } catch (err) {
    console.error("Erreur notifications:", err);
  } finally {
    loading.value = false;
  }
};

const togglePanel = () => {
  open.value = !open.value;
  if (open.value && notifications.value.length === 0) {
    refresh();
  }
};

const markAsRead = async (notificationId: number) => {
  try {
    const updated = await apiFetch(`/notifications/${notificationId}/read`, {
      method: "PATCH"
    });
    notifications.value = notifications.value.map((item) =>
      item.id === notificationId ? updated : item
    );
  } catch (err) {
    console.error("Erreur notification read:", err);
  }
};

const deleteNotification = async (notificationId: number) => {
  if (!confirm('Supprimer cette notification ?')) return;
  try {
    await apiFetch(`/notifications/${notificationId}`, {
      method: "DELETE"
    });
    notifications.value = notifications.value.filter((item) => item.id !== notificationId);
  } catch (err: any) {
    console.error("Erreur suppression notification:", err);
    alert(err?.data?.detail || "Erreur lors de la suppression");
  }
};

const respondToInvitation = async (notification: any, status: 'ACCEPTED' | 'DECLINED') => {
  const invitationId = notification.data;
  if (!invitationId) return;
  
  responding.value[invitationId] = status;
  try {
    await apiFetch(`/invitations/${invitationId}`, {
      method: "PATCH",
      body: { status }
    });
    // Marquer la notification comme lue
    await markAsRead(notification.id);
    // Rafraîchir pour voir les changements
    await refresh();
    alert(status === 'ACCEPTED' ? 'Invitation acceptée !' : 'Invitation refusée.');
  } catch (err: any) {
    console.error("Erreur réponse invitation:", err);
    alert(err?.data?.detail || "Erreur lors de la réponse à l'invitation");
  } finally {
    responding.value[invitationId] = null;
  }
};

onMounted(() => {
  if (isAuthenticated.value) {
    refresh();
  }
});
</script>

<style scoped>
.notification-bell {
  position: relative;
  display: inline-block;
  z-index: 9999;
}

.badge {
  display: inline-block;
  margin-left: 0.4rem;
  background: var(--accent);
  color: #fff;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.notification-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
  padding: 1rem;
  width: 360px;
  z-index: 10000;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.8rem;
}

.notification-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-actions {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.btn.mini {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}

.btn.mini.danger {
  background: #ef4444;
  color: white;
}

.btn.mini.danger:hover {
  background: #dc2626;
}

.invitation-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 0.8rem;
  border-left: 3px solid var(--accent);
}

.invitation-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.invitation-status {
  margin-top: 0.6rem;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
}

.status-accepted {
  color: #059669;
  background: #d1fae5;
}

.status-declined {
  color: #dc2626;
  background: #fee2e2;
}
</style>
