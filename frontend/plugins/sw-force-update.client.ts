// Plugin pour forcer la mise à jour du Service Worker
export default defineNuxtPlugin(() => {
  if (process.client && 'serviceWorker' in navigator) {
    // Écouter les messages du SW
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data?.type === 'SW_UPDATED') {
        console.log('[SW] Nouvelle version détectée:', event.data.version);
        // Rafraîchir la page pour utiliser le nouveau SW
        window.location.reload();
      }
    });

    // Vérifier les mises à jour du SW
    navigator.serviceWorker.ready.then((registration) => {
      console.log('[SW] Ready, checking for updates...');
      
      // Forcer la vérification de mise à jour
      registration.update();
      
      // Écouter les nouveaux SW en attente
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          console.log('[SW] Nouveau worker trouvé');
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('[SW] Nouvelle version installée, rechargement...');
              window.location.reload();
            }
          });
        }
      });
    });

    // Désinscrire l'ancien SW s'il existe (une seule fois par navigateur)
    const SW_CLEANUP_KEY = 'sw_cleanup_done_v1';
    if (!localStorage.getItem(SW_CLEANUP_KEY)) {
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        let unregisteredCount = 0;
        registrations.forEach((registration) => {
          if (registration.scope.includes('proximeet')) {
            console.log('[SW] Found registration:', registration.scope);
            registration.unregister().then(() => {
              console.log('[SW] Unregistered old SW');
            });
            unregisteredCount++;
          }
        });
        if (unregisteredCount > 0) {
          console.log('[SW] Cleanup done, marking as completed');
        }
        localStorage.setItem(SW_CLEANUP_KEY, 'true');
      });
    } else {
      console.log('[SW] Cleanup already done, skipping');
    }
  }
});
