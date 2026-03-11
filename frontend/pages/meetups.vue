<template>
  <section class="section">
    <div class="card">
      <h2 class="section-title">Creer un meetup</h2>
      <div class="field">
        <label>Restaurant ID (optionnel)</label>
        <input v-model="form.restaurant_id" placeholder="place_id" />
      </div>
      <div class="field">
        <label>Rayon (km)</label>
        <select v-model.number="form.radius_km">
          <option :value="1">1</option>
          <option :value="2">2</option>
          <option :value="3">3</option>
          <option :value="5">5</option>
        </select>
      </div>
      <div class="field">
        <label>Date et heure</label>
        <input v-model="form.scheduled_at" type="datetime-local" />
      </div>
      <button class="btn" @click="createMeetup">Creer</button>
    </div>

    <div class="card">
      <h2 class="section-title">Meetups</h2>
      <button class="btn secondary" @click="loadMeetups">Rafraichir</button>
      <div class="card-grid" style="margin-top:1rem;">
        <div class="card" v-for="meetup in meetups" :key="meetup.id">
          <strong>Meetup #{{ meetup.id }}</strong>
          <p class="mono">Restaurant: {{ meetup.restaurant_id || "Libre" }}</p>
          <p class="mono">Rayon: {{ meetup.radius_km }} km</p>
          <p class="mono">Date: {{ new Date(meetup.scheduled_at).toLocaleString() }}</p>
          <p class="mono">Statut: {{ meetup.status }}</p>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
            <button class="btn secondary" @click="updateStatus(meetup.id, 'COMPLETED')">Termine</button>
            <button class="btn secondary" @click="updateStatus(meetup.id, 'CANCELLED')">Annuler</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const { token, acquireToken, handleRedirect } = useAuth();
const meetups = ref<any[]>([]);
const form = reactive({
  restaurant_id: "",
  radius_km: 1,
  scheduled_at: ""
});

const apiFetch = async (path: string, options: any = {}) => {
  await handleRedirect();
  const accessToken = token.value || (await acquireToken());
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  return $fetch(`${config.public.apiBase}${path}`, { ...options, headers });
};

const loadMeetups = async (skip = 0, limit = 20) => {
  const data = await apiFetch(`/meetups?skip=${skip}&limit=${limit}`);
  meetups.value = data.items || [];
};

const createMeetup = async () => {
  await apiFetch("/meetups", {
    method: "POST",
    body: {
      restaurant_id: form.restaurant_id || null,
      radius_km: form.radius_km,
      scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : new Date().toISOString()
    }
  });
  await loadMeetups();
};

const updateStatus = async (id: number, status: string) => {
  await apiFetch(`/meetups/${id}`, {
    method: "PATCH",
    body: { status }
  });
  await loadMeetups();
};

onMounted(loadMeetups);
</script>
