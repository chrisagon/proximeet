// Composable pour gérer l'état de la connexion réseau
export const useNetworkStatus = () => {
  const isOnline = ref(true);
  const isOffline = computed(() => !isOnline.value);

  if (process.client) {
    isOnline.value = navigator.onLine;

    const updateOnlineStatus = () => {
      isOnline.value = navigator.onLine;
      console.log('[Network] Status changed:', isOnline.value ? 'online' : 'offline');
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    onUnmounted(() => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    });
  }

  return {
    isOnline,
    isOffline
  };
};
