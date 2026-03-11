<template>
  <section class="stepper">
    <div class="stepper__header">
      <div class="stepper__track">
        <div class="stepper__progress" :style="{ width: `${progress}%` }"></div>
      </div>
      <div class="stepper__labels">
        <div
          v-for="(step, index) in steps"
          :key="step.title"
          class="stepper__step"
          :class="{ active: index <= activeIndex }"
        >
          <span class="stepper__dot"></span>
          <div>
            <p class="mono stepper__index">Etape {{ index + 1 }}</p>
            <strong>{{ step.title }}</strong>
            <p v-if="step.subtitle" class="stepper__subtitle">{{ step.subtitle }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="stepper__content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

type Step = {
  title: string;
  subtitle?: string;
};

const props = defineProps<{
  steps: Step[];
  activeIndex: number;
}>();

const progress = computed(() => {
  if (!props.steps.length) return 0;
  if (props.steps.length === 1) return 100;
  return Math.round((props.activeIndex / (props.steps.length - 1)) * 100);
});
</script>

<style scoped>
.stepper {
  display: grid;
  gap: 1.5rem;
}

.stepper__header {
  display: grid;
  gap: 1.2rem;
}

.stepper__track {
  position: relative;
  height: 10px;
  border-radius: 999px;
  background: rgba(15, 27, 45, 0.1);
  overflow: hidden;
}

.stepper__progress {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--sea));
  transition: width 0.4s ease;
}

.stepper__labels {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.stepper__step {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  padding: 0.6rem 0.8rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(15, 27, 45, 0.08);
  box-shadow: 0 10px 20px var(--shadow);
  transition: transform 0.3s ease, background 0.3s ease;
}

.stepper__step.active {
  background: #ffffff;
  transform: translateY(-2px);
}

.stepper__dot {
  width: 12px;
  height: 12px;
  margin-top: 0.4rem;
  border-radius: 50%;
  background: rgba(15, 27, 45, 0.2);
  box-shadow: 0 0 0 4px rgba(255, 122, 89, 0.15);
}

.stepper__step.active .stepper__dot {
  background: var(--accent);
  box-shadow: 0 0 0 6px rgba(255, 122, 89, 0.2);
}

.stepper__index {
  margin: 0 0 0.2rem;
  color: var(--sea);
}

.stepper__subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.9rem;
  color: rgba(15, 27, 45, 0.7);
}

.stepper__content {
  background: #ffffff;
  border-radius: 22px;
  padding: 2rem;
  border: 1px solid rgba(15, 27, 45, 0.08);
  box-shadow: 0 18px 36px var(--shadow);
  animation: fadeUp 0.4s ease;
}

@media (max-width: 720px) {
  .stepper__labels {
    grid-template-columns: 1fr;
  }
}
</style>
