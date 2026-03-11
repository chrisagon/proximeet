<template>
  <section class="section">
    <div class="card">
      <h1 style="margin:0; font-size:1.5rem;">📅 Mon Agenda</h1>
      <p class="mono" style="margin:0.5rem 0 0 0; color:var(--sea);">Vos invitations acceptées</p>
    </div>

    <!-- ClientOnly pour éviter l'hydratation mismatch -->
    <ClientOnly>
      <!-- Calendrier -->
      <div class="card">
      <div class="calendar-toolbar">
        <h2 class="section-title" style="margin: 0;">
          {{ currentMonthYear }}
        </h2>
        <div class="calendar-nav">
          <button class="btn mini secondary" @click="previousMonth">◀</button>
          <button class="btn mini secondary" @click="goToToday">Aujourd'hui</button>
          <button class="btn mini secondary" @click="nextMonth">▶</button>
        </div>
      </div>

      <!-- Grille du calendrier -->
      <div class="calendar-grid">
        <!-- Jours de la semaine -->
        <div class="calendar-header" v-for="day in weekDays" :key="day">
          {{ day }}
        </div>
        
        <!-- Jours du mois -->
        <div 
          v-for="date in calendarDays" 
          :key="date.date.toISOString()"
          class="calendar-day"
          :class="{ 
            'today': isToday(date.date),
            'other-month': !isCurrentMonth(date.date),
            'has-event': hasEvent(date.date)
          }"
        >
          <span class="day-label">{{ getWeekdayLabel(date.date) }}</span>
          <span class="day-number">{{ date.date.getDate() }}</span>
          
          <!-- Événements du jour -->
          <div class="day-events">
            <div 
              v-for="invitation in getEventsForDate(date.date)" 
              :key="invitation.id"
              class="event-item"
              @click="showEventDetails(invitation)"
            >
              {{ invitation.restaurant_name || 'Restaurant' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Rendez-vous sans date fixée -->
    <div v-if="acceptedInvitationsNoDate.length > 0" class="card" style="border-left: 3px solid #f59e0b;">
      <h2 class="section-title">⏳ Rendez-vous sans date fixée</h2>
      <p class="mono" style="color: #666; margin-bottom: 1rem;">
        Ces invitations sont acceptées mais n'ont pas de date programmée.
      </p>
      <div class="card-grid">
        <div 
          class="card" 
          v-for="invitation in acceptedInvitationsNoDate" 
          :key="invitation.id"
          style="border-left: 3px solid #f59e0b;"
        >
          <div style="display: flex; justify-content: space-between; align-items: start;">
            <strong>📍 {{ invitation.restaurant_name || 'Restaurant' }}</strong>
            <span class="mono" style="color: #f59e0b; font-size: 0.8rem;">Pas de date</span>
          </div>
          <p class="mono" style="margin-top: 0.5rem;">
            <template v-if="invitation.organizer_name && invitation.organizer_name.includes('(invité)')">
              👤 Avec: {{ invitation.organizer_name.replace(' (invité)', '') }}
              <span style="color: #3b82f6; font-size: 0.75rem;">(Vous êtes l'organisateur)</span>
            </template>
            <template v-else>
              👤 Organisé par: {{ invitation.organizer_name || invitation.organizer_email || 'Quelqu\'un' }}
            </template>
          </p>
          <p class="mono" v-if="invitation.message" style="margin-top: 0.5rem; font-style: italic; color: #666;">
            💬 "{{ invitation.message }}"
          </p>
        </div>
      </div>
    </div>

    <!-- Liste des invitations acceptées -->
    <div class="card">
      <h2 class="section-title">📋 Détails des rendez-vous programmés</h2>
      
      <div v-if="loading" class="mono">Chargement...</div>
      <div v-else-if="acceptedInvitations.length === 0 && acceptedInvitationsNoDate.length === 0" class="mono">
        Aucune invitation acceptée.
      </div>
      <div v-else-if="sortedAcceptedInvitations.length === 0" class="mono">
        Aucun rendez-vous programmé avec une date.
      </div>
      <div v-else class="card-grid">
        <div 
          class="card" 
          v-for="invitation in sortedAcceptedInvitations" 
          :key="invitation.id"
          style="border-left: 3px solid #22c55e;"
        >
          <div style="display: flex; justify-content: space-between; align-items: start;">
            <strong>✅ {{ invitation.restaurant_name || 'Restaurant' }}</strong>
            <span class="mono" style="color: #22c55e; font-size: 0.8rem;">
              {{ formatDate(invitation.scheduled_at) }}
            </span>
          </div>
          
          <p class="mono" style="margin-top: 0.5rem; color: #666;">
            📍 <NuxtLink :to="`/restaurants/${invitation.restaurant_id}`">{{ invitation.restaurant_name || 'Restaurant' }}</NuxtLink>
          </p>
          
          <p class="mono" style="margin-top: 0.3rem;">
            🕐 {{ formatTime(invitation.scheduled_at) }}
          </p>
          
          <p class="mono" style="margin-top: 0.3rem;">
            <template v-if="invitation.organizer_name && invitation.organizer_name.includes('(invité)')">
              👤 Avec: {{ invitation.organizer_name.replace(' (invité)', '') }}
              <span style="color: #3b82f6; font-size: 0.75rem;">(Vous êtes l'organisateur)</span>
            </template>
            <template v-else>
              👤 Organisé par: {{ invitation.organizer_name || invitation.organizer_email || 'Quelqu\'un' }}
            </template>
          </p>
          
          <p class="mono" v-if="invitation.message" style="margin-top: 0.5rem; font-style: italic; color: #666;">
            💬 "{{ invitation.message }}"
          </p>
          
          <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
            <button class="btn mini secondary" @click="addToCalendar(invitation)">
              📥 Ajouter à mon calendrier
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal détails -->
    <div v-if="selectedEvent" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ selectedEvent.restaurant_name }}</h3>
        <p><strong>Date :</strong> {{ formatDate(selectedEvent.scheduled_at) }}</p>
        <p><strong>Heure :</strong> {{ formatTime(selectedEvent.scheduled_at) }}</p>
        <p><strong>Avec :</strong> {{ selectedEvent.organizer_name }}</p>
        <p v-if="selectedEvent.message"><strong>Message :</strong> {{ selectedEvent.message }}</p>
        <div class="modal-actions">
          <button class="btn" @click="addToCalendar(selectedEvent)">Ajouter à mon calendrier</button>
          <button class="btn secondary" @click="closeModal">Fermer</button>
        </div>
      </div>
    </div>
    </ClientOnly>
  </section>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();

const loading = ref(false);
const invitations = ref<any[]>([]);
const selectedEvent = ref<any>(null);

// Calendrier
const currentDate = ref(new Date());
const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

const currentMonthYear = computed(() => {
  const month = currentDate.value.toLocaleDateString('fr-FR', { month: 'long' });
  const year = currentDate.value.getFullYear();
  return `${month.charAt(0).toUpperCase() + month.slice(1)} ${year}`;
});

const acceptedInvitations = computed(() => 
  invitations.value.filter(inv => inv.status === 'ACCEPTED' && inv.scheduled_at)
);

const acceptedInvitationsNoDate = computed(() => 
  invitations.value.filter(inv => inv.status === 'ACCEPTED' && !inv.scheduled_at)
);

const sortedAcceptedInvitations = computed(() => {
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  return [...acceptedInvitations.value]
    .filter(inv => {
      const scheduledAt = new Date(inv.scheduled_at);
      return scheduledAt.getTime() >= startOfToday.getTime();
    })
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
});

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  // Trouver le premier lundi
  let startDate = new Date(firstDay);
  const dayOfWeek = firstDay.getDay();
  const daysFromMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
  startDate.setDate(firstDay.getDate() - daysFromMonday);
  
  // Générer 42 jours (6 semaines)
  const days = [];
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    days.push({ date });
  }
  
  return days;
});

const apiFetch = async (path: string, options: any = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
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

const loadInvitations = async () => {
  loading.value = true;
  try {
    // Utiliser le nouvel endpoint pour récupérer toutes les invitations acceptées
    // (en tant qu'invité ET en tant qu'organisateur)
    const timestamp = Date.now();
    const data = await apiFetch(`/invitations/accepted-meetings?_t=${timestamp}`);
    console.log("[Calendar] Accepted meetings loaded:", data);
    console.log("[Calendar] Total accepted count:", data.length);
    invitations.value = data;
  } catch (err: any) {
    console.error("Erreur chargement invitations:", err);
  } finally {
    loading.value = false;
  }
};

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
};

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
};

const goToToday = () => {
  currentDate.value = new Date();
};

const isToday = (date: Date) => {
  const today = new Date();
  return date.toDateString() === today.toDateString();
};

const isCurrentMonth = (date: Date) => {
  return date.getMonth() === currentDate.value.getMonth();
};

const hasEvent = (date: Date) => {
  return acceptedInvitations.value.some(inv => {
    if (!inv.scheduled_at) return false;
    const invDate = new Date(inv.scheduled_at);
    return invDate.toDateString() === date.toDateString();
  });
};

const getWeekdayLabel = (date: Date) => {
  const dayIndex = date.getDay();
  const weekIndex = dayIndex === 0 ? 6 : dayIndex - 1;
  return weekDays[weekIndex];
};

const getEventsForDate = (date: Date) => {
  return acceptedInvitations.value.filter(inv => {
    if (!inv.scheduled_at) return false;
    const invDate = new Date(inv.scheduled_at);
    return invDate.toDateString() === date.toDateString();
  });
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'Date non définie';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const formatTime = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const showEventDetails = (invitation: any) => {
  selectedEvent.value = invitation;
};

const closeModal = () => {
  selectedEvent.value = null;
};

const addToCalendar = (invitation: any) => {
  // Générer un fichier .ics pour téléchargement
  const startDate = new Date(invitation.scheduled_at);
  const endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000); // +2h par défaut
  
  const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}
DTEND:${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}
SUMMARY:Invitation Proximeet - ${invitation.restaurant_name}
DESCRIPTION:Organisé par ${invitation.organizer_name || invitation.organizer_email}\\n${invitation.message || ''}
LOCATION:${invitation.restaurant_name}
END:VEVENT
END:VCALENDAR`;

  const blob = new Blob([icsContent], { type: 'text/calendar' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `invitation-${invitation.id}.ics`;
  link.click();
  URL.revokeObjectURL(url);
  
  alert('Fichier calendrier téléchargé ! Importez-le dans votre application de calendrier.');
};

// Charger immédiatement si on est côté client
if (process.client) {
  loadInvitations();
}

onMounted(() => {
  loadInvitations();
});

onActivated(() => {
  loadInvitations();
});
</script>

<style scoped>
.calendar-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.calendar-nav {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.calendar-grid {
  --calendar-cols: 7;
  display: grid;
  grid-template-columns: repeat(var(--calendar-cols), minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
}

.calendar-header {
  text-align: center;
  font-weight: bold;
  color: var(--sea);
  padding: 0.5rem;
  font-size: 0.9rem;
}

.calendar-day {
  min-height: 80px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.5rem;
  position: relative;
  background: white;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.calendar-day:hover {
  background: #f8fafc;
}

.calendar-day.today {
  background: #eff6ff;
  border-color: #3b82f6;
}

.calendar-day.other-month {
  color: #9ca3af;
  background: #f9fafb;
}

.calendar-day.has-event {
  border-left: 3px solid #22c55e;
}

.day-number {
  font-size: 0.875rem;
  font-weight: 500;
}

.day-label {
  display: none;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--sea);
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.event-item {
  background: #22c55e;
  color: white;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.7rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.event-item:hover {
  background: #16a34a;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  margin-top: 0;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .calendar-grid {
    --calendar-cols: 3;
    gap: 0.25rem;
  }
  
  .calendar-day {
    min-height: 50px;
    padding: 0.25rem;
    gap: 0.2rem;
  }
  
  .day-number {
    font-size: 0.75rem;
  }
  
  .event-item {
    font-size: 0.6rem;
    padding: 0.1rem 0.25rem;
  }

  .modal-content {
    max-width: 340px;
    padding: 1.1rem;
  }
}

@media (max-width: 480px) {
  .calendar-grid {
    --calendar-cols: 1;
  }

  .calendar-header {
    display: none;
  }

  .calendar-day {
    min-height: 64px;
    padding: 0.6rem;
  }

  .day-label {
    display: inline-block;
  }

  .event-item {
    white-space: normal;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .modal-content {
    width: 94%;
    max-width: 320px;
    padding: 1rem;
    font-size: 0.95rem;
  }

  .modal-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
