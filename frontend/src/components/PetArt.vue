<script setup>
// The couple's pet: the dog art cropped from task/ui-source (Dog-Growth.png).
import { art } from '@/characters.js'

defineProps({
  stage: { type: Number, default: 2 },       // 0 baby, 1 growing, 2 adult
  mood: { type: String, default: 'neutral' }, // neutral | happy | shy | excited
  face: Boolean,                              // head only (avatars, chips)
})
</script>

<template>
  <img class="pet-art" :src="art[face ? `male-${mood}` : `male-${stage + 1}`]" alt="" />
</template>
