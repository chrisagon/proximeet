<template>
  <Transition name="fade">
    <div v-if="isOffline" class="offline-banner">
      <span class="offline-icon">📡</span>
      <span>Mode hors ligne - Les données peuvent être en cache</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const { isOffline } = useNetworkStatus();
</script>

<style scoped>
.offline-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  color: #fff;
  padding: 0.6rem 1rem;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.offline-icon {
  font-size: 1rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
