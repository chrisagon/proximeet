<template>
  <div v-if="open" class="modal-backdrop">
    <div class="modal-card">
      <div class="modal-header">
        <h3 style="margin:0;">Inviter {{ inviteeName || 'un collegue' }}</h3>
        <button class="btn mini" @click="$emit('close')">Fermer</button>
      </div>
      <div class="field">
        <label>Restaurant favori</label>
        <select v-model="selectedRestaurantId">
          <option value="">-- Choisir --</option>
          <option v-for="fav in favorites" :key="fav.restaurant.place_id" :value="fav.restaurant.place_id">
            {{ fav.restaurant.name }}
          </option>
        </select>
        <p v-if="favorites.length === 0" class="mono">Vous n'avez aucun favori pour le moment.</p>
      </div>
      <div class="field" style="background: #fff7ed; padding: 1rem; border-radius: 8px; border: 2px solid #fdba74;">
        <label style="color: #c2410c; font-weight: 600;">📅 Date et heure du rendez-vous *</label>
        <input
          v-model="scheduledAt"
          type="datetime-local"
          style="border-color: #fdba74;"
          :min="todayISO"
          required
        />
        <p class="mono" style="font-size: 0.8rem; color: #c2410c; margin-top: 0.5rem;">
          <strong>Obligatoire</strong> - Sans date, l'invitation n'apparaîtra pas dans l'agenda
        </p>
      </div>
      <div class="field">
        <label>Message</label>
        <textarea v-model="message" placeholder="Un petit mot pour l'invitation..."></textarea>
      </div>
      <p v-if="error" class="mono" style="color: var(--accent);">{{ error }}</p>
      <div class="modal-actions">
        <button class="btn" :disabled="!selectedRestaurantId || !scheduledAt" @click="submit">
          Envoyer l'invitation
        </button>
        <button class="btn secondary" @click="$emit('close')">Annuler</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  open: { type: Boolean, default: false },
  inviteeName: { type: String, default: "" },
  favorites: { type: Array as () => any[], default: () => [] },
  error: { type: String, default: "" }
});

const emit = defineEmits(["close", "send"]);

const selectedRestaurantId = ref("");
const message = ref("");
const scheduledAt = ref("");
const todayISO = computed(() => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
});

const isPastDate = (value: string) => {
  if (!value) return false;
  const datePart = value.slice(0, 10);
  return datePart < todayISO.value;
};

const submit = () => {
  if (!scheduledAt.value) {
    alert("La date et heure du rendez-vous sont obligatoires !");
    return;
  }
  if (isPastDate(scheduledAt.value)) {
    alert("La date du rendez-vous ne peut pas être dans le passé.");
    return;
  }
  emit("send", {
    restaurant_id: selectedRestaurantId.value,
    message: message.value,
    scheduled_at: new Date(scheduledAt.value).toISOString()
  });
};

watch(
  () => props.open,
  (value) => {
    if (value) {
      selectedRestaurantId.value = "";
      message.value = "";
      scheduledAt.value = "";
    }
  }
);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  width: min(520px, 92vw);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
}

.btn.mini {
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
}
</style>
