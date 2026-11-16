<script setup>
import { computed } from 'vue'
const props = defineProps({
  color: { type: String, default: '#FBE5DD' },
  emojis: { type: Array, default: () => [] },
  large: Boolean,
})
const shown = computed(() => props.emojis.slice(0, props.large ? 6 : 5))
</script>

<template>
  <div class="jar-art" :class="{ large }" :style="{ '--jar-color': color }" aria-hidden="true">
    <svg viewBox="0 0 120 140">
      <path class="jar-glass" d="M32 40h56v8q22 4 22 26v46q0 14-14 14H24q-14 0-14-14V74q0-22 22-26Z" />
      <path class="jar-shine" d="M21 76q0-12 10-18M19 90v22M101 82v12" />
      <path class="jar-cloth" d="M18 42Q20 20 60 18q40 2 42 24l2 4q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0q-4 5-8 0Z" />
      <path class="jar-cloth-fold" d="M38 23q3 9 1 19M60 19v23M82 23q-3 9-1 19" />
      <rect class="jar-band" x="22" y="42" width="76" height="6" rx="3" />
      <path class="jar-bow" d="M60 45C48 32 36 38 43 48c4 5 12 1 17-3Zm0 0c12-13 24-7 17 3-4 5-12 1-17-3Zm-2 2-6 13 4-1 4-10Zm4 0 6 13-4-1-4-10Z" />
      <circle class="jar-knot" cx="60" cy="45" r="3.5" />
    </svg>
    <div class="jar-emojis"><span v-for="(emoji, i) in shown" :key="i">{{ emoji }}</span></div>
  </div>
</template>
