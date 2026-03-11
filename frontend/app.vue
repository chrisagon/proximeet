<template>
  <div class="app-wrapper">
    <OfflineIndicator />
    
    <!-- Fixed Header - Only for authenticated users (not on landing page) -->
    <header v-if="showFixedHeader" class="fixed-header" role="banner">
      <div class="header-inner">
        <!-- Logo -->
        <NuxtLink class="header-logo" to="/dashboard">
          <span class="logo-mark">◉</span>
          <span class="logo-name">Proximeet</span>
        </NuxtLink>
        
        <!-- Desktop Navigation -->
        <nav class="header-nav" role="navigation">
          <NuxtLink 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path"
            :class="['nav-link', { active: isActive(item.path) }]"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </NuxtLink>
        </nav>
        
        <!-- Actions -->
        <div class="header-actions">
          <NotificationBell v-if="isAuthenticated" />
          <button class="btn-icon" @click="showHelp = true" title="Aide ?">
            <span>?</span>
          </button>
          <button v-if="isAuthenticated" class="btn-logout" @click="handleLogout">
            <span class="logout-icon">⎋</span>
            <span class="logout-text">Déconnexion</span>
          </button>
        </div>
        
        <!-- Mobile Menu Toggle -->
        <button 
          class="mobile-menu-toggle" 
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-expanded="mobileMenuOpen"
          aria-label="Menu"
        >
          <span class="menu-line" :class="{ open: mobileMenuOpen }"></span>
          <span class="menu-line" :class="{ open: mobileMenuOpen }"></span>
          <span class="menu-line" :class="{ open: mobileMenuOpen }"></span>
        </button>
      </div>
      
      <!-- Mobile Navigation Dropdown -->
      <Transition name="slide-down">
        <nav v-if="mobileMenuOpen && showFixedHeader" class="mobile-nav" role="navigation">
          <NuxtLink 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path"
            :class="['mobile-nav-link', { active: isActive(item.path) }]"
            @click="mobileMenuOpen = false"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </NuxtLink>
          <div class="mobile-nav-actions">
            <button class="mobile-nav-btn" @click="showHelp = true; mobileMenuOpen = false">
              <span>❓</span> Aide
            </button>
            <button v-if="isAuthenticated" class="mobile-nav-btn mobile-logout" @click="handleLogout">
              <span>⎋</span> Déconnexion
            </button>
          </div>
        </nav>
      </Transition>
    </header>
    
    <!-- Main Content -->
    <main :class="['main-content', { 'with-header': showFixedHeader }]">
      <NuxtPage />
    </main>
    
    <!-- Help Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
          <div class="modal-card">
            <button class="modal-close" @click="showHelp = false" aria-label="Fermer">×</button>
            <div class="modal-content">
              <h3 class="modal-title">
                <span class="modal-icon">💡</span>
                Comment utiliser Proximeet
              </h3>
              <ol class="help-steps">
                <li>
                  <span class="step-badge">1</span>
                  <p>Choisissez d'abord un ou plusieurs restaurants favoris à proximité en cliquant sur <strong>Restaurants</strong>.</p>
                </li>
                <li>
                  <span class="step-badge">2</span>
                  <p>Aller dans <strong>Tableau de bord</strong> : définissez votre position et cliquez sur "Recherche de proximité".</p>
                </li>
                <li>
                  <span class="step-badge">3</span>
                  <p>Choisissez un des collègues à proximité.</p>
                </li>
                <li>
                  <span class="step-badge">4</span>
                  <p>Définissez le jour et l'heure dans un de vos restaurants favoris.</p>
                </li>
                <li>
                  <span class="step-badge">5</span>
                  <p>Votre collègue accepte le rendez-vous.</p>
                </li>
                <li>
                  <span class="step-badge">6</span>
                  <p>Le rendez-vous apparaît dans votre agenda.</p>
                </li>
              </ol>
              <button class="btn-modal" @click="showHelp = false">J'ai compris</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
const { token, setToken } = useAuth();
const router = useRouter();
const route = useRoute();

// State
const mobileMenuOpen = ref(false);
const showHelp = ref(false);
const isAuthChecking = ref(true);

// Check authentication
const isAuthenticated = computed(() => !!token.value);

// Show fixed header only on authenticated pages
const showFixedHeader = computed(() => {
  // Don't show on landing page (root) and auth pages
  if (route.path === '/') return false;
  return isAuthenticated.value;
});

// Navigation items
const navItems = [
  { path: '/dashboard', label: 'Tableau de bord', icon: '🏠' },
  { path: '/calendar', label: 'Agenda', icon: '📅' },
  { path: '/restaurants', label: 'Restaurants', icon: '🍽️' },
];

// Check active route
const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(`${path}/`);
};

// Close mobile menu on route change
watch(() => route.path, () => {
  mobileMenuOpen.value = false;
});

// Close mobile menu on escape key
onMounted(() => {
  if (process.client) {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        mobileMenuOpen.value = false;
        showHelp.value = false;
      }
    });
    
    // Check auth state
    isAuthChecking.value = false;
    
    // Register Service Worker for PWA
    registerSW();
  }
});

// Register Service Worker for PWA
const registerSW = () => {
  if (process.client && 'serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered:', registration.scope);
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error);
      });
  }
};

// Handle logout
const handleLogout = () => {
  if (confirm("Voulez-vous vraiment vous déconnecter ?")) {
    setToken(null);
    mobileMenuOpen.value = false;
    
    if (process.client) {
      localStorage.removeItem("onboarding_completed");
      localStorage.removeItem("user_profile");
      localStorage.removeItem("user_preferences");
    }
    
    router.push("/");
  }
};

// Meta
useHead({
  title: 'Proximeet',
  meta: [
    { name: 'description', content: 'Déjeuner connecté, proximité sereine' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1' }
  ]
});
</script>

<style>
/* Global styles */
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap");

:root {
  --ink: #0f1b2d;
  --mist: #f8f6f1;
  --accent: #ff7a59;
  --accent-dark: #d65a3a;
  --sea: #56a3a6;
  --sand: #f3d9b1;
  --shadow: rgba(15, 27, 45, 0.12);
  --header-height: 70px;
  --header-height-mobile: 64px;
}

* {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
}

body {
  font-family: "Space Grotesk", "Segoe UI", -apple-system, sans-serif;
  background: var(--mist);
  color: var(--ink);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  line-height: 1.5;
}

a {
  color: inherit;
  text-decoration: none;
}

/* App Wrapper */
.app-wrapper {
  min-height: 100vh;
}

/* Fixed Header */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(15, 27, 45, 0.07);
  box-shadow: 0 2px 10px rgba(15, 27, 45, 0.06);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 1rem;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.logo-mark {
  color: var(--accent);
  font-size: 1.4rem;
  font-weight: 700;
}

.logo-name {
  font-family: "IBM Plex Mono", monospace;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--ink);
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex: 1;
  justify-content: center;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  color: #64748b;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--ink);
  background: rgba(15, 27, 45, 0.04);
}

.nav-link.active {
  color: var(--accent);
  background: rgba(255, 122, 89, 0.08);
}

.nav-icon {
  font-size: 1.1rem;
}

.nav-label {
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-icon {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(15, 27, 45, 0.12);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(15, 27, 45, 0.05);
  color: var(--ink);
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border: 1px solid rgba(15, 27, 45, 0.12);
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  font-family: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.btn-logout:hover {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.logout-icon {
  font-size: 1.1rem;
}

.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 44px;
  height: 44px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.menu-line {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--ink);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.menu-line.open:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.menu-line.open:nth-child(2) {
  opacity: 0;
}

.menu-line.open:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* Mobile Navigation */
.mobile-nav {
  display: none;
  background: rgba(255, 255, 255, 0.99);
  border-top: 1px solid rgba(15, 27, 45, 0.07);
  padding: 0.5rem 1rem;
  max-height: calc(100vh - var(--header-height));
  overflow-y: auto;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 10px;
  color: #64748b;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.mobile-nav-link:hover,
.mobile-nav-link.active {
  color: var(--accent);
  background: rgba(255, 122, 89, 0.06);
}

.mobile-nav-actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(15, 27, 45, 0.07);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mobile-nav-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: #64748b;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  width: 100%;
}

.mobile-nav-btn:hover {
  background: rgba(15, 27, 45, 0.04);
}

.mobile-logout {
  color: #ef4444;
}

/* Main Content */
.main-content {
  min-height: 100vh;
}

.main-content.with-header {
  padding-top: var(--header-height);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 27, 45, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(15, 27, 45, 0.25);
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(15, 27, 45, 0.06);
  border-radius: 50%;
  font-size: 1.5rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 1;
}

.modal-close:hover {
  background: rgba(15, 27, 45, 0.12);
  color: var(--ink);
}

.modal-content {
  padding: 2rem;
  overflow-y: auto;
  max-height: 90vh;
}

.modal-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-icon {
  font-size: 1.5rem;
}

.help-steps {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.help-steps li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 10px;
}

.step-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.help-steps p {
  margin: 0;
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.5;
}

.help-steps strong {
  color: var(--ink);
}

.btn-modal {
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
}

.btn-modal:hover {
  transform: translateY(-1px);
  opacity: 0.95;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .header-inner {
    height: var(--header-height-mobile);
    padding: 0 1rem;
  }
  
  .header-nav {
    display: none;
  }
  
  .mobile-menu-toggle {
    display: flex;
  }
  
  .mobile-nav {
    display: flex;
    flex-direction: column;
  }
  
  .header-actions .btn-logout {
    display: none;
  }
  
  .main-content.with-header {
    padding-top: var(--header-height-mobile);
  }
  
  .modal-card {
    border-radius: 16px;
  }
  
  .modal-content {
    padding: 1.5rem;
  }
  
  .modal-title {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .logo-name {
    display: none;
  }
  
  .modal-content {
    padding: 1.25rem;
  }
}

/* Print styles */
@media print {
  .fixed-header {
    display: none;
  }
  
  .main-content.with-header {
    padding-top: 0;
  }
}
</style>
