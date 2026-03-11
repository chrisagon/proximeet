// Service Worker Proximeet - v5 (fix chrome-extension)
const CACHE_NAME = 'proximeet-v5-cache';
const STATIC_ASSETS = [
  '/',
  '/login',
  '/signup',
  '/dashboard',
  '/restaurants',
  '/meetups',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Forcer la mise à jour immédiate
self.addEventListener('install', (event) => {
  console.log('[SW v4] Installation forcée...');
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW v4] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).catch((err) => {
      console.error('[SW v4] Cache failed:', err);
    })
  );
});

// Activation - nettoyer TOUS les anciens caches et prendre contrôle
self.addEventListener('activate', (event) => {
  console.log('[SW v4] Activation forcée...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log('[SW v4] Deleting old cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    }).then(() => {
      // Envoyer un message à tous les clients pour rafraîchir
      return self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          client.postMessage({ type: 'SW_UPDATED', version: 'v4' });
        });
      });
    })
  );
});

// Gestion des requêtes - PAS DE CACHE POUR L'API
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Ignorer les requêtes non-HTTP (chrome-extension, etc.)
  if (!request.url.startsWith('http')) {
    return;
  }
  
  const url = new URL(request.url);

  // API calls : PAS DE CACHE du tout
  if (url.pathname.startsWith('/api/') || request.url.includes('8000')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({ error: 'Offline', items: [], total: 0 }),
          { headers: { 'Content-Type': 'application/json' }, status: 503 }
        );
      })
    );
    return;
  }

  // Static assets : Cache First
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response.status === 200 && 
            ['image', 'script', 'style'].includes(request.destination)) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      }).catch(() => {
        if (request.destination === 'image') {
          return new Response('', { status: 204 });
        }
        return new Response('Offline', { status: 503 });
      });
    })
  );
});

// Messages du client
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    event.waitUntil(
      self.registration.showNotification(data.title || 'Proximeet', {
        body: data.body || 'Nouvelle notification',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        data: data.url || '/'
      })
    );
  }
});
