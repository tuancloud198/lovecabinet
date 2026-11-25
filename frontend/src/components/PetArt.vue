<script setup>
// The couple's pet (dog, or the cat bought in the shop): the stage's body with the mood's head on it,
// drawn as one SVG so it sizes like an image. `face`: the head alone (chips, mood picker). Shows the
// pet being previewed in the shop, else the couple's own; the `species` prop overrides both.
import { computed } from 'vue'
import { PETS } from '@/characters.js'
import { state } from '@/store.js'

const props = defineProps({
  species: String,
  stage: { type: Number, default: 2 },  // 0 baby, 1 growing, 2 adult
  mood: { type: String, default: '' },  // neutral | happy | shy | excited ('' = neutral)
  face: Boolean,                        // head only
})
const pet = computed(() => PETS[props.species || state.preview?.pet || state.couple?.pet_type] || PETS.dog)
const head = computed(() => pet.value.heads[props.mood] || pet.value.heads.neutral)
// The head's box on the body, in body pixels (anchors are % of the body image).
const layout = computed(() => {
  const { bodySizes, headSize, anchors } = pet.value
  const [W, H] = bodySizes[props.stage]
  const a = anchors[props.stage]
  const w = (a.w / 100) * W
  const h = (w * headSize[1]) / headSize[0]
  const x = (a.x / 100) * W
  const y = (a.y / 100) * H
  return { W, H, x, y, w, h, transform: a.r ? `rotate(${a.r} ${x + w / 2} ${y + h / 2})` : undefined }
})
</script>

<template>
  <img v-if="face" class="pet-art" :src="head" alt="" />
  <svg v-else class="pet-art" :viewBox="`0 0 ${layout.W} ${layout.H}`" xmlns="http://www.w3.org/2000/svg">
    <image :href="pet.bodies[stage]" :width="layout.W" :height="layout.H" />
    <image :href="head" :x="layout.x" :y="layout.y" :width="layout.w" :height="layout.h" :transform="layout.transform" />
  </svg>
</template>
