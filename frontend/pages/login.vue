<template>
  <section class="section login">
    <div class="card login-card">
      <div class="login-hero">
        <p class="mono">PROXIMEET</p>
        <h2>Connexion</h2>
        <p>Retrouvez votre équipe et partagez votre présence.</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="field">
          <label>Email</label>
          <input 
            v-model="form.email" 
            type="email" 
            required 
            autocomplete="email"
            placeholder="vous@exemple.fr"
          />
        </div>
        
        <div class="field">
          <label>Mot de passe (optionnel en mode anonyme)</label>
          <input 
            v-model="form.password" 
            type="password" 
            autocomplete="current-password"
          />
        </div>

        <p v-if="error" class="mono error">{{ error }}</p>
        
        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>

        <div style="text-align:center; margin-top:1rem;">
          <p class="mono" style="font-size:0.9rem;">
            Pas encore de compte ?
            <NuxtLink to="/signup" style="color:var(--accent); text-decoration:underline;">
              S'inscrire
            </NuxtLink>
          </p>
        </div>
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
  password: ""
});

const loading = ref(false);
const error = ref<string | null>(null);

// Redirection si déjà connecté
onMounted(() => {
  if (process.client) {
    const { token } = useAuth();
    const { hasCompletedOnboarding } = useOnboardingCheck();
    
    if (token.value) {
      const redirectPath = hasCompletedOnboarding() ? "/dashboard" : "/onboarding";
      router.replace(redirectPath);
    }
  }
});

const handleLogin = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.post<{ user: any; token: string }>("/auth/login", {
      email: form.email,
      password: form.password || undefined
    });
    
    setToken(response.token);
    
    if (process.client) {
      localStorage.setItem("user_profile", JSON.stringify(response.user));
      const { hasCompletedOnboarding } = useOnboardingCheck();
      
      const redirectPath = hasCompletedOnboarding() ? "/dashboard" : "/onboarding";
      await router.push(redirectPath);
    }
  } catch (err: any) {
    error.value = err?.message || "Email ou mot de passe incorrect";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-card {
  max-width: 500px;
  margin: 0 auto;
  display: grid;
  gap: 2rem;
}

.login-hero {
  text-align: center;
  padding: 1.6rem;
  background: linear-gradient(135deg, rgba(86, 163, 166, 0.18), rgba(255, 122, 89, 0.18));
  border-radius: 18px;
  border: 1px solid rgba(15, 27, 45, 0.08);
}

.login-hero h2 {
  margin: 0.5rem 0;
}

.login-form {
  display: grid;
  gap: 1.2rem;
}

.error {
  color: var(--accent);
  padding: 0.8rem;
  background: rgba(255, 122, 89, 0.1);
  border-radius: 10px;
  border: 1px solid var(--accent);
}
</style>
