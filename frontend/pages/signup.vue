<template>
  <section class="section signup">
    <div class="card signup-card">
      <div class="signup-hero">
        <p class="mono">PROXIMEET</p>
        <h2>Creer votre compte</h2>
        <p>
          Rejoignez votre equipe, partagez votre presence en toute confiance
          et trouvez des collegues a proximite.
        </p>
      </div>

      <form class="signup-form" @submit.prevent="handleSignup">
        <div class="field">
          <label>Email</label>
          <input v-model="form.email" type="email" required autocomplete="email" />
        </div>
        <div class="field">
          <label>Prenom</label>
          <input v-model="form.first_name" type="text" required autocomplete="given-name" />
        </div>
        <div class="field">
          <label>Nom</label>
          <input v-model="form.last_name" type="text" required autocomplete="family-name" />
        </div>
        <div class="field">
          <label>Pseudo (optionnel)</label>
          <input v-model="form.nickname" type="text" autocomplete="nickname" />
        </div>
        <div class="field">
          <label>Mot de passe (optionnel)</label>
          <input v-model="form.password" type="password" autocomplete="new-password" />
        </div>

        <div class="avatar-block">
          <div class="field">
            <label>Avatar (upload)</label>
            <input type="file" accept="image/*" @change="handleAvatarFile" />
          </div>
          <div class="field">
            <label>Avatar (URL)</label>
            <input v-model="form.avatar_url" type="url" placeholder="https://..." />
          </div>
          <div v-if="avatarPreview" class="avatar-preview">
            <img :src="avatarPreview" alt="Apercu avatar" />
          </div>
        </div>

        <p v-if="error" class="mono error">{{ error }}</p>
        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? 'Creation...' : 'Continuer vers l\'onboarding' }}
        </button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
const api = useApi();
const { setToken } = useAuth();
const router = useRouter();

const form = reactive({
  email: "",
  first_name: "",
  last_name: "",
  nickname: "",
  password: "",
  avatar_url: ""
});

const avatarPreview = ref<string | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

onMounted(() => {
  if (!process.client) return;
  const { hasCompletedOnboarding } = useOnboardingCheck();
  if (hasCompletedOnboarding()) {
    router.replace("/dashboard");
  }
});

const handleAvatarFile = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    avatarPreview.value = String(reader.result || "");
  };
  reader.readAsDataURL(file);
};

const handleSignup = async () => {
  loading.value = true;
  error.value = null;
  try {
    const payload = {
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
      nickname: form.nickname || undefined,
      password: form.password || undefined,
      avatar_url: avatarPreview.value || form.avatar_url || undefined
    };
    const response = await api.post<{ user: any; token: string }>("/auth/signup", payload);
    setToken(response.token);
    if (process.client) {
      localStorage.setItem("onboarding_completed", "false");
      localStorage.setItem("user_profile", JSON.stringify(response.user));
    }
    await router.push("/onboarding");
  } catch (err: any) {
    error.value = err?.message || "Impossible de creer le compte";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.signup-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}

.signup-hero {
  background: linear-gradient(135deg, rgba(86, 163, 166, 0.18), rgba(255, 122, 89, 0.18));
  border-radius: 18px;
  padding: 1.6rem;
  border: 1px solid rgba(15, 27, 45, 0.08);
}

.signup-form {
  display: grid;
  gap: 1rem;
}

.avatar-block {
  display: grid;
  gap: 0.8rem;
  padding: 1rem;
  border-radius: 16px;
  background: rgba(15, 27, 45, 0.03);
  border: 1px dashed rgba(15, 27, 45, 0.15);
}

.avatar-preview {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #fff;
  box-shadow: 0 10px 20px var(--shadow);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.error {
  color: var(--accent);
}
</style>
