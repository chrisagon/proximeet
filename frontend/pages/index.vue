<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-logo">
        <svg class="logo-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="24" cy="24" r="22" fill="#ff7a59" opacity="0.15"/>
          <circle cx="24" cy="24" r="18" fill="#ff7a59" opacity="0.2"/>
          <path d="M24 12C24 12 32 20 32 28C32 32.4 28.4 36 24 36C19.6 36 16 32.4 16 28C16 20 24 12 24 12Z" fill="#ff7a59"/>
          <circle cx="24" cy="26" r="4" fill="#fff"/>
        </svg>
        <h1 class="logo-text">PROXIMEET</h1>
      </div>
      <h2 class="hero-tagline">Déjeuner connecté, proximité sereine.</h2>
      <p class="hero-description">
        Partage une présence éphémère, trouve tes collègues à proximité, et lance des meetups autour des meilleures adresses.
      </p>
    </section>

    <!-- Fonctions clés -->
    <section class="features-section">
      <h3 class="section-title">Fonctions clés</h3>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">📍</div>
          <p>Présence 72h, précise ou en mode bubble.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <p>Recherche par rayon 1 à 20 km.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⭐</div>
          <p>Recommandations et habitudes officielles.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🤝</div>
          <p>Meetups organisés en un clic.</p>
        </div>
      </div>
    </section>

    <!-- Comment utiliser -->
    <section class="how-to-section">
      <h3 class="section-title">Comment utiliser Proximeet</h3>
      <div class="steps-list">
        <div class="step-item">
          <span class="step-number">1</span>
          <p>Choisissez d'abord un ou plusieurs restaurants favoris à proximité en cliquant sur <strong>Restaurants</strong>.</p>
        </div>
        <div class="step-item">
          <span class="step-number">2</span>
          <p>Aller dans <strong>Tableau de bord</strong> : définissez votre position et cliquez sur "Recherche de proximité".</p>
        </div>
        <div class="step-item">
          <span class="step-number">3</span>
          <p>Choisissez un des collègues à proximité.</p>
        </div>
        <div class="step-item">
          <span class="step-number">4</span>
          <p>Définissez le jour et l'heure dans un de vos restaurants favoris.</p>
        </div>
        <div class="step-item">
          <span class="step-number">5</span>
          <p>Votre collègue accepte le rendez-vous.</p>
        </div>
        <div class="step-item">
          <span class="step-number">6</span>
          <p>Le rendez-vous apparaît dans votre agenda.</p>
        </div>
      </div>
    </section>

    <!-- Login Section -->
    <section class="login-section">
      <div class="login-card">
        <h3 class="login-title">Accéder à Proximeet</h3>
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
            <label>Mot de passe</label>
            <input 
              v-model="form.password" 
              type="password" 
              autocomplete="current-password"
              placeholder="Votre mot de passe"
            />
          </div>

          <p v-if="error" class="error-message">{{ error }}</p>
          
          <button class="btn btn-primary" type="submit" :disabled="loading">
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>

          <div class="login-links">
            <p class="signup-link">
              Pas encore de compte ?
              <NuxtLink to="/signup" class="link-accent">
                S'inscrire
              </NuxtLink>
            </p>
            <NuxtLink to="/restaurants" class="link-secondary">
              Découvrir les restaurants →
            </NuxtLink>
          </div>
        </form>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <p class="mono">© 2025 Proximeet — Déjeuner connecté</p>
    </footer>
  </div>
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
      navigateTo(redirectPath);
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
.landing-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f6f1 0%, #fff 50%, #f8f6f1 100%);
  padding: 0;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 5rem 1.5rem 4rem;
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(255, 122, 89, 0.08) 0%, rgba(86, 163, 166, 0.08) 100%);
  border-radius: 0 0 50% 50% / 0 0 10% 10%;
}

.hero-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.logo-icon {
  width: 100px;
  height: 100px;
  filter: drop-shadow(0 4px 12px rgba(255, 122, 89, 0.3));
}

.logo-text {
  font-family: "IBM Plex Mono", monospace;
  font-size: 1.8rem;
  letter-spacing: 0.35em;
  color: #0f1b2d;
  margin: 0;
  font-weight: 600;
}

.hero-tagline {
  font-size: clamp(1.8rem, 5vw, 2.8rem);
  font-weight: 600;
  color: #0f1b2d;
  margin: 0 0 1.2rem;
  line-height: 1.2;
}

.hero-description {
  font-size: 1.15rem;
  color: #4a5568;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.7;
}

/* Features Section */
.features-section {
  padding: 4rem 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  color: #0f1b2d;
  margin-bottom: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.2rem;
}

@media (min-width: 640px) {
  .features-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.feature-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem 1rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(15, 27, 45, 0.08);
  border: 1px solid rgba(15, 27, 45, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(15, 27, 45, 0.12);
}

.feature-icon {
  font-size: 2.2rem;
  margin-bottom: 1rem;
}

.feature-card p {
  margin: 0;
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* How To Section */
.how-to-section {
  padding: 3rem 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: #fff;
  padding: 1.2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(15, 27, 45, 0.06);
  border: 1px solid rgba(15, 27, 45, 0.05);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #ff7a59 0%, #ff5a3a 100%);
  color: #fff;
  font-weight: 600;
  border-radius: 50%;
  flex-shrink: 0;
  font-size: 0.95rem;
}

.step-item p {
  margin: 0;
  color: #4a5568;
  line-height: 1.5;
  font-size: 0.95rem;
}

.step-item p strong {
  color: #0f1b2d;
}

/* Login Section */
.login-section {
  padding: 3rem 1.5rem;
  display: flex;
  justify-content: center;
}

.login-card {
  background: linear-gradient(135deg, #0f1b2d 0%, #1a2d47 100%);
  border-radius: 24px;
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 12px 40px rgba(15, 27, 45, 0.25);
  color: #fff;
}

.login-title {
  text-align: center;
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #fff;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-size: 0.85rem;
  color: #a0aec0;
  font-weight: 500;
}

.field input {
  padding: 0.9rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.field input::placeholder {
  color: #718096;
}

.field input:focus {
  outline: none;
  border-color: #ff7a59;
  box-shadow: 0 0 0 3px rgba(255, 122, 89, 0.15);
}

.error-message {
  color: #ff7a59;
  font-size: 0.9rem;
  text-align: center;
  padding: 0.8rem;
  background: rgba(255, 122, 89, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 122, 89, 0.3);
}

.btn {
  padding: 1rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #ff7a59 0%, #ff5a3a 100%);
  color: #fff;
  margin-top: 0.5rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  opacity: 0.95;
}

.login-links {
  text-align: center;
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.signup-link {
  margin: 0;
  font-size: 0.9rem;
  color: #a0aec0;
}

.link-accent {
  color: #ff7a59;
  text-decoration: none;
  font-weight: 500;
}

.link-accent:hover {
  text-decoration: underline;
}

.link-secondary {
  color: #56a3a6;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
}

.link-secondary:hover {
  text-decoration: underline;
}

/* Footer */
.landing-footer {
  text-align: center;
  padding: 3rem 1.5rem;
  background: #f8f6f1;
}

.landing-footer .mono {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.85rem;
  color: #718096;
  margin: 0;
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .hero-section {
    padding: 4rem 1.5rem 3rem;
  }
  
  .logo-icon {
    width: 80px;
    height: 80px;
  }
  
  .logo-text {
    font-size: 1.5rem;
    letter-spacing: 0.25em;
  }
  
  .hero-tagline {
    font-size: 1.6rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .features-section {
    padding: 3rem 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 1.2rem 1rem;
  }
  
  .login-card {
    padding: 2rem 1.5rem;
  }
  
  .step-item {
    padding: 1rem;
  }
  
  .step-number {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
}
</style>
