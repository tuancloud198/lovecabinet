<script setup>
// The couple's pet. Dogs use the character art cropped from task/ui-source; cats and capybaras
// are drawn here in the same style (thick dark outline, sleepy eyes, rosy cheeks, grass patch).
import { computed } from 'vue'
import { art } from '@/characters.js'

const props = defineProps({
  species: { type: String, default: 'dog' }, // dog | cat | capybara
  stage: { type: Number, default: 2 },       // 0 baby, 1 growing, 2 adult
  mood: { type: String, default: 'neutral' }, // neutral | happy | shy | excited
  face: Boolean,                              // head only (avatars, chips)
})

const OUTLINE = '#3B2A22'
const PALETTES = {
  cat: { body: '#F7C98B', belly: '#FFF1DC', mark: '#DE9650', ear: '#F6A9A3' },
  capybara: { body: '#C98F5E', belly: '#D9A577', mark: '#9C6842', ear: '#9C6842', muzzle: '#B07A4E' },
}
const c = computed(() => PALETTES[props.species])
const bodyScale = computed(() => [0.7, 0.85, 1][props.stage] ?? 1)
const headScale = computed(() => [0.9, 0.95, 1][props.stage] ?? 1)
// Body is drawn for an adult standing on y = 160 with its neck at y = 100.
const headY = computed(() => 160 - 60 * bodyScale.value - 26 * headScale.value)
const openMouth = computed(() => props.mood === 'happy' || props.mood === 'excited')
</script>

<template>
  <img v-if="species === 'dog'" class="pet-art" :src="art[face ? `male-${mood}` : `male-${stage + 1}`]" alt="" />
  <svg v-else class="pet-art" :viewBox="face ? '-52 -66 104 104' : '30 4 140 166'" aria-hidden="true"
       :stroke="OUTLINE" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
    <!-- Ground, body and tail (full figure only) -->
    <g v-if="!face">
      <ellipse cx="100" cy="161" rx="66" ry="8" fill="#D3E6B0" stroke="none" />
      <path d="M44 160q2-10 6-14M52 160q0-7 4-10M150 160q-1-9-6-13M158 160q0-6-3-9" stroke="#9CC46B" stroke-width="3" fill="none" />
      <g :transform="`translate(100 160) scale(${bodyScale}) translate(-100 -160)`">
        <template v-if="species === 'cat'">
          <path d="M126 150c32 2 34-32 20-38" fill="none" :stroke="OUTLINE" stroke-width="15" />
          <path d="M126 150c32 2 34-32 20-38" fill="none" :stroke="c.body" stroke-width="8" />
          <path d="M70 160c-6-32 6-58 30-60 24 2 36 28 30 60Z" :fill="c.body" />
          <path d="M86 160c-2-24 6-40 14-40s16 16 14 40Z" :fill="c.belly" stroke="none" />
          <path d="M73 128q7 2 9 9M127 128q-7 2-9 9M75 142q6 1 8 6M125 142q-6 1-8 6" :stroke="c.mark" fill="none" />
          <ellipse cx="88" cy="157" rx="10" ry="6" :fill="c.body" /><ellipse cx="112" cy="157" rx="10" ry="6" :fill="c.body" />
          <path d="M85 155v4M91 155v4M109 155v4M115 155v4" stroke-width="1.8" />
        </template>
        <template v-else>
          <path d="M54 160c-6-40 16-62 46-62s52 22 46 62Z" :fill="c.body" />
          <path d="M80 160c0-22 8-34 20-34s20 12 20 34Z" :fill="c.belly" stroke="none" />
          <path d="M62 132q5-6 12-6M138 132q-5-6-12-6" :stroke="c.mark" fill="none" />
          <ellipse cx="80" cy="158" rx="11" ry="5.5" :fill="c.mark" /><ellipse cx="120" cy="158" rx="11" ry="5.5" :fill="c.mark" />
        </template>
      </g>
      <path v-if="mood === 'excited' || mood === 'happy'" :transform="`translate(0 ${headY - 78})`"
            d="M44 52l8 6M40 66l10 2M58 40l3 9" stroke="#F5C12E" stroke-width="5" fill="none" />
    </g>

    <!-- Head, centred on (0, 0) -->
    <g :transform="face ? '' : `translate(100 ${headY}) scale(${headScale})`">
      <template v-if="species === 'cat'">
        <path d="M-37-12-33-52-9-31Z" :fill="c.body" /><path d="M37-12 33-52 9-31Z" :fill="c.body" />
        <path d="M-31-20-29-43-15-30Z" :fill="c.ear" stroke="none" /><path d="M31-20 29-43 15-30Z" :fill="c.ear" stroke="none" />
        <ellipse rx="43" ry="34" :fill="c.body" />
        <path d="M-6-33v9M0-34v11M6-33v9" :stroke="c.mark" stroke-width="3" fill="none" />
        <!-- pink bow on the left ear, like Cún Nón Lá's flower -->
        <g transform="translate(-26 -36) rotate(-20)"><path d="M0 0-12-7v14ZM0 0l12-7v14Z" fill="#F28FA0" stroke-width="2" /><circle r="3.5" fill="#E86F86" stroke-width="2" /></g>
        <path d="M-31 6h-14M-31 11l-13 5M31 6h14M31 11l13 5" stroke-width="1.8" fill="none" />
        <path d="M-4 3h8l-4 4Z" fill="#E88A8A" stroke-width="2" />
      </template>
      <template v-else>
        <ellipse cx="-27" cy="-36" rx="8" ry="6.5" :fill="c.ear" /><ellipse cx="27" cy="-36" rx="8" ry="6.5" :fill="c.ear" />
        <rect x="-37" y="-40" width="74" height="72" rx="28" :fill="c.body" />
        <rect x="-25" y="-2" width="50" height="31" rx="15" :fill="c.muzzle" stroke="none" />
        <ellipse cx="-8" cy="8" rx="2.6" ry="3.6" :fill="OUTLINE" stroke="none" /><ellipse cx="8" cy="8" rx="2.6" ry="3.6" :fill="OUTLINE" stroke="none" />
        <path d="M-4-40v-5M2-40v-6" stroke-width="2.5" fill="none" />
        <!-- the classic capybara mandarin -->
        <circle cy="-50" r="10" fill="#F5A33B" /><path d="M0-60q8-9 15-4-6 9-15 4Z" fill="#7DB35A" stroke-width="2" />
      </template>

      <!-- Cheeks -->
      <ellipse cx="-25" cy="10" rx="7" ry="4.5" fill="#F4A6A0" opacity=".75" stroke="none" />
      <ellipse cx="25" cy="10" rx="7" ry="4.5" fill="#F4A6A0" opacity=".75" stroke="none" />
      <path v-if="mood === 'shy'" d="M-31 9l4-5M-26 10l4-5M-21 11l4-5M19 11l4-5M24 10l4-5M29 9l4-5" stroke="#E46F6F" stroke-width="1.8" fill="none" />

      <!-- Eyes -->
      <g v-if="mood === 'neutral' || mood === 'shy'">
        <ellipse cx="-16" cy="-8" rx="8" ry="7" fill="#fff" stroke-width="2.5" /><ellipse cx="16" cy="-8" rx="8" ry="7" fill="#fff" stroke-width="2.5" />
        <circle :cx="mood === 'shy' ? -12 : -15" cy="-5" r="3.2" :fill="OUTLINE" stroke="none" /><circle :cx="mood === 'shy' ? 20 : 17" cy="-5" r="3.2" :fill="OUTLINE" stroke="none" />
        <path v-if="mood === 'neutral'" d="M-24-8a8 7 0 0 1 16 0ZM8-8a8 7 0 0 1 16 0Z" :fill="c.body" stroke-width="2.5" />
      </g>
      <path v-else-if="mood === 'happy'" d="M-23-6q7-9 14 0M9-6q7-9 14 0" stroke-width="3" fill="none" />
      <path v-else d="M-24-14l12 6-12 6M24-14l-12 6 12 6" stroke-width="3" fill="none" />

      <!-- Mouth -->
      <template v-if="openMouth">
        <path :d="species === 'cat' ? 'M-8 10q8 13 16 0Z' : 'M-7 17q7 11 14 0Z'" fill="#8A3B33" stroke-width="2.5" />
        <ellipse :cy="species === 'cat' ? 16.5 : 22.5" rx="4" ry="2.8" fill="#F28B8B" stroke="none" />
      </template>
      <path v-else-if="species === 'cat'" :d="mood === 'shy' ? 'M-5 13q2.5-2 5 0t5 0' : 'M-8 11q4 4 8 0 4 4 8 0'" stroke-width="2.5" fill="none" />
      <path v-else :d="mood === 'shy' ? 'M-4 21q2-2 4 0t4 0' : 'M-6 20q6 4 12 0'" stroke-width="2.5" fill="none" />
    </g>
  </svg>
</template>
