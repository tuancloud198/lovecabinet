<script setup>
import { computed, useId } from 'vue'
import EmojiIcon from '@/components/EmojiIcon.vue'
// The memory jar (design system "Hũ kỷ niệm"): wooden lid, a ribbon bow in the jar's colour, clear glass,
// and the memories' emoji in white bubbles inside (up to 6, three per row).
const props = defineProps({
  color: { type: String, default: '#F6C9C4' },
  emojis: { type: Array, default: () => [] },
  large: Boolean,
})
const shown = computed(() => props.emojis.slice(0, 6))
const glassId = `jar-glass-${useId()}`
</script>

<template>
  <div class="jar-art" :class="{ large }" :style="{ '--jar-color': color }" aria-hidden="true">
    <svg viewBox="0 0 120 136">
      <defs>
        <linearGradient :id="glassId" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stop-color="#fff" stop-opacity=".82" />
          <stop offset=".22" stop-color="#FFFDFA" stop-opacity=".62" />
          <stop offset=".78" stop-color="#FFFDFA" stop-opacity=".58" />
          <stop offset="1" stop-color="#fff" stop-opacity=".78" />
        </linearGradient>
      </defs>
      <path class="jar-glass" :fill="`url(#${glassId})`" d="M26 19H94V33Q94 39 103 43Q116 50 116 67V118Q116 134 100 134H20Q4 134 4 118V67Q4 50 17 43Q26 39 26 33Z" />
      <path class="jar-rim" d="M26 19H94V33Q94 39 103 43Q116 50 116 67V118Q116 134 100 134H20Q4 134 4 118V67Q4 50 17 43Q26 39 26 33Z" />
      <path class="jar-shine" d="M11 69Q12 55 25 49" />
      <path class="jar-shine thin" d="M10.5 79V99M109 73V83" />
      <path class="jar-lid-side" d="M27.5 8.5V23A32.5 6.5 0 0 0 92.5 23V8.5Z" />
      <path class="jar-lid-grain" d="M35 14V25.5M43 14V27.3M51.5 14V28.2M60 14V28.5M68.5 14V28.2M77 14V27.3M85 14V25.5" />
      <ellipse class="jar-lid-top" cx="60" cy="8.5" rx="32.5" ry="6.5" />
      <path class="jar-lid-grain top" d="M36 8.5Q60 2.5 84 8.5M43 5.8Q60 10.8 77 5.8M60 3v11" />
      <path class="jar-ribbon" d="M24 28.5Q60 36.5 96 28.5V36.5Q60 44.5 24 36.5Q22.5 32.5 24 28.5Z" />
      <path class="jar-ribbon-shine" d="M27 31.5Q60 38.5 93 31.5" />
      <path class="jar-ribbon" d="M82 37Q78 51 71 62L76.5 60.5L79 66Q85 52 87.5 38Z" />
      <path class="jar-ribbon" d="M86 37Q96 48 104 61L105 55.5L110.5 56Q100 45 90 35Z" />
      <path class="jar-ribbon" d="M84 34C76 21 59 21 59 30C59 40 75 42 84 34Z" />
      <path class="jar-ribbon" d="M84 34C90 20 110 17 111 27C112 38 94 42 84 34Z" />
      <path class="jar-ribbon-fold" d="M80.5 33Q71 27.5 63 29.5M88 32.5Q97 25 106 25.5M79.5 36Q72 38.5 66 37M89 36Q97 39 104 36" />
      <rect class="jar-knot" x="79.5" y="29.5" width="9" height="9" rx="3" />
    </svg>
    <div class="jar-emojis">
      <span v-for="(emoji, i) in shown" :key="i" class="jar-bubble"><EmojiIcon :emoji="emoji" /></span>
    </div>
  </div>
</template>
