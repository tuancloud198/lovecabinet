<script setup>
// The couple's pet. Dogs use the character art cropped from task/ui-source; cats and capybaras
// are drawn here in the same style (thick dark outline, rosy cheeks, grass patch). The capybara is a
// chubby sitting capy: wide flat-topped head, big boxy muzzle, small bead eyes, mandarin on top.
// The honey badger is dark with its silver-white cape over the head and shoulders, and white claws.
// The hamster is a chubby golden ball with puffy cream cheeks, holding a sunflower seed.
import { computed } from 'vue'
import { art } from '@/characters.js'

const props = defineProps({
  species: { type: String, default: 'dog' }, // dog | cat | capybara | honey_badger | hamster
  stage: { type: Number, default: 2 },       // 0 baby, 1 growing, 2 adult
  mood: { type: String, default: 'neutral' }, // neutral | happy | shy | excited
  face: Boolean,                              // head only (avatars, chips)
})

const OUTLINE = '#3B2A22'
const PALETTES = {
  cat: { body: '#F7C98B', belly: '#FFF1DC', mark: '#DE9650', ear: '#F6A9A3' },
  hamster: { body: '#F2BE4E', belly: '#FFF2D6', mark: '#D99A2B', ear: '#F2BE4E', muzzle: '#FFF2D6', paw: '#F7B9A8' },
  honey_badger: { body: '#4E4948', cape: '#ECE6DA', belly: '#6A6462', mark: '#3A3635', ear: '#4E4948', muzzle: '#857D7A', paw: '#3A3635' },
  capybara: { body: '#C58A57', belly: '#E6BC8F', mark: '#8A5833', ear: '#8A5833', muzzle: '#D8A271', paw: '#9E6A41' },
}
const c = computed(() => PALETTES[props.species])
const bodyScale = computed(() => [0.7, 0.85, 1][props.stage] ?? 1)
const headScale = computed(() => [0.9, 0.95, 1][props.stage] ?? 1)
// Body is drawn for an adult standing on y = 160 with its neck at y = 100.
const headY = computed(() => 160 - 60 * bodyScale.value - 26 * headScale.value + (props.species === 'capybara' ? 6 : 0))
// Capybara and honey badger have small bead eyes; the badger's dark fur needs light eye lines.
const beady = computed(() => ['capybara', 'honey_badger', 'hamster'].includes(props.species))
const EYES = { honey_badger: { x: 17, y: -4, ink: '#F1ECE2' }, hamster: { x: 19, y: -9, ink: OUTLINE } }
const eye = computed(() => EYES[props.species] ?? { x: 24, y: -15, ink: OUTLINE })
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
        <template v-else-if="species === 'hamster'">
          <path d="M52 160c-8-34 12-60 48-62 36 2 56 28 48 62Z" :fill="c.body" />
          <path d="M70 160c-4-26 10-42 30-42s34 16 30 42Z" :fill="c.belly" stroke="none" />
          <!-- sunflower seed held in both paws -->
          <path d="M100 122c7 4 8 16 0 22-8-6-7-18 0-22Z" fill="#4A4342" stroke-width="2.5" /><path d="M100 126v14" stroke="#E8E1D6" stroke-width="2" />
          <ellipse cx="86" cy="138" rx="6.5" ry="7.5" :fill="c.paw" /><ellipse cx="114" cy="138" rx="6.5" ry="7.5" :fill="c.paw" />
          <ellipse cx="80" cy="157" rx="11" ry="5.5" :fill="c.paw" /><ellipse cx="120" cy="157" rx="11" ry="5.5" :fill="c.paw" />
          <path d="M77 154v4M83 154v4M117 154v4M123 154v4" stroke-width="1.6" />
        </template>
        <template v-else-if="species === 'honey_badger'">
          <path d="M140 152c14-1 19-12 14-19" fill="none" :stroke="OUTLINE" stroke-width="13" />
          <path d="M140 152c14-1 19-12 14-19" fill="none" :stroke="c.body" stroke-width="6" />
          <path d="M56 160c-6-30 10-56 44-58 34 2 50 28 44 58Z" :fill="c.body" />
          <!-- silver cape over the shoulders (outline redrawn on top) -->
          <path d="M59 132c5-19 19-29 41-30 22 1 36 11 41 30-10-9-24-13-41-13s-31 4-41 13Z" :fill="c.cape" stroke="none" />
          <path d="M56 160c-6-30 10-56 44-58 34 2 50 28 44 58" fill="none" />
          <path d="M80 160c-2-20 8-32 20-32s22 12 20 32Z" :fill="c.belly" stroke="none" />
          <ellipse cx="86" cy="138" rx="7" ry="9" :fill="c.body" /><ellipse cx="114" cy="138" rx="7" ry="9" :fill="c.body" />
          <ellipse cx="77" cy="157" rx="13" ry="6" :fill="c.paw" /><ellipse cx="123" cy="157" rx="13" ry="6" :fill="c.paw" />
          <!-- the famous claws -->
          <path d="M82 146l-1 4M86 147v4M90 146l1 4M110 146l-1 4M114 147v4M118 146l1 4M70 160l-2 3M76 161v3M82 160l2 3M118 160l-2 3M124 161v3M130 160l2 3" :stroke="c.cape" stroke-width="2" />
        </template>
        <template v-else>
          <!-- chubby sitting body, wider at the bottom -->
          <path d="M50 160c-7-32 12-58 50-60 38 2 57 28 50 60Z" :fill="c.body" />
          <path d="M74 160c-3-22 8-36 26-36s29 14 26 36Z" :fill="c.belly" stroke="none" />
          <path d="M60 140q3-6 9-8M140 140q-3-6-9-8" :stroke="c.mark" stroke-width="2.4" fill="none" />
          <!-- little front paws on the belly -->
          <ellipse cx="86" cy="137" rx="7" ry="9" :fill="c.body" /><ellipse cx="114" cy="137" rx="7" ry="9" :fill="c.body" />
          <path d="M83 144v-3M89 144v-3M111 144v-3M117 144v-3" stroke-width="1.6" />
          <!-- feet -->
          <ellipse cx="76" cy="157" rx="13" ry="6" :fill="c.paw" /><ellipse cx="124" cy="157" rx="13" ry="6" :fill="c.paw" />
          <path d="M72 154v4M78 154v4M122 154v4M128 154v4" stroke-width="1.6" />
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
      <template v-else-if="species === 'hamster'">
        <circle cx="-29" cy="-27" r="10" :fill="c.ear" /><circle cx="29" cy="-27" r="10" :fill="c.ear" />
        <circle cx="-29" cy="-27" r="5" fill="#F7B9A8" stroke="none" /><circle cx="29" cy="-27" r="5" fill="#F7B9A8" stroke="none" />
        <ellipse rx="44" ry="34" :fill="c.body" />
        <!-- cream face with puffy cheek pouches -->
        <path d="M-40 10c0-12 12-18 24-16 6-8 26-8 32 0 12-2 24 4 24 16 0 14-18 23-40 23s-40-9-40-23Z" :fill="c.belly" stroke="none" />
        <path d="M-6-34q2 6 0 12M6-34q-2 6 0 12" :stroke="c.mark" stroke-width="2.4" fill="none" />
        <ellipse cy="2" rx="4.5" ry="3.2" fill="#F08C8C" stroke-width="2" />
      </template>
      <template v-else-if="species === 'honey_badger'">
        <circle cx="-33" cy="-19" r="7.5" :fill="c.body" /><circle cx="33" cy="-19" r="7.5" :fill="c.body" />
        <ellipse rx="42" ry="33" :fill="c.body" />
        <!-- silver-white cape from the forehead back (outline redrawn on top) -->
        <path d="M-42-2C-42-21-24-33 0-33S42-21 42-2C30-11 16-16 0-16S-30-11-42-2Z" :fill="c.cape" stroke="none" />
        <ellipse rx="42" ry="33" fill="none" />
        <ellipse cy="12" rx="19" ry="13" :fill="c.muzzle" stroke="none" />
        <ellipse cy="5" rx="7.5" ry="4.8" fill="#1E1A1A" stroke="none" /><ellipse cx="-2.5" cy="3.6" rx="2" ry="1.2" fill="#6F6866" stroke="none" />
      </template>
      <template v-else>
        <!-- small ears tucked on top -->
        <ellipse cx="-27" cy="-33" rx="6.5" ry="5" :fill="c.ear" /><ellipse cx="27" cy="-33" rx="6.5" ry="5" :fill="c.ear" />
        <!-- boxy head with a long, blunt snout -->
        <path d="M-40-6c0-20 12-30 40-30s40 10 40 30v8c0 20-16 30-40 30s-40-10-40-30Z" :fill="c.body" />
        <path d="M-21 12c0-14 7-20 21-20s21 6 21 20-9 18-21 18-21-6-21-18Z" :fill="c.muzzle" stroke="none" />
        <!-- big dark capybara nose with nostrils -->
        <path d="M-13-1c0-5 6-7 13-7s13 2 13 7-6 9-13 9-13-4-13-9Z" fill="#5B3A27" stroke="none" />
        <ellipse cx="-6" cy="-2" rx="2.4" ry="1.6" fill="#8C6046" stroke="none" /><ellipse cx="6" cy="-2" rx="2.4" ry="1.6" fill="#8C6046" stroke="none" />
        <path d="M-12-31q3-4 7-4M2-36q2-3 5-3" :stroke="c.mark" stroke-width="2.2" fill="none" />
        <!-- the classic capybara mandarin -->
        <circle cy="-45" r="10" fill="#F5A33B" /><path d="M0-55q8-9 15-4-6 9-15 4Z" fill="#7DB35A" stroke-width="2" />
        <circle cx="-3" cy="-48" r="2" fill="#FFD27F" stroke="none" />
      </template>

      <!-- Cheeks -->
      <ellipse :cx="species === 'cat' ? -25 : -29" :cy="species === 'cat' ? 10 : species === 'capybara' ? 4 : 9" rx="7" ry="4.5" fill="#F4A6A0" opacity=".75" stroke="none" />
      <ellipse :cx="species === 'cat' ? 25 : 29" :cy="species === 'cat' ? 10 : species === 'capybara' ? 4 : 9" rx="7" ry="4.5" fill="#F4A6A0" opacity=".75" stroke="none" />
      <path v-if="mood === 'shy'" d="M-31 9l4-5M-26 10l4-5M-21 11l4-5M19 11l4-5M24 10l4-5M29 9l4-5" stroke="#E46F6F" stroke-width="1.8" fill="none" />

      <!-- Eyes -->
      <g v-if="beady && (mood === 'neutral' || mood === 'shy')">
        <template v-if="species === 'honey_badger'"><circle :cx="-eye.x" :cy="eye.y" r="6.6" :fill="eye.ink" stroke="none" /><circle :cx="eye.x" :cy="eye.y" r="6.6" :fill="eye.ink" stroke="none" /></template>
        <ellipse :cx="-eye.x + (mood === 'shy' ? 2 : 0)" :cy="eye.y" rx="4" ry="4.8" :fill="OUTLINE" stroke="none" />
        <ellipse :cx="eye.x + (mood === 'shy' ? 2 : 0)" :cy="eye.y" rx="4" ry="4.8" :fill="OUTLINE" stroke="none" />
        <circle :cx="-eye.x + 1.4 + (mood === 'shy' ? 2 : 0)" :cy="eye.y - 2" r="1.5" fill="#fff" stroke="none" /><circle :cx="eye.x + 1.4 + (mood === 'shy' ? 2 : 0)" :cy="eye.y - 2" r="1.5" fill="#fff" stroke="none" />
      </g>
      <path v-else-if="beady && mood === 'happy'" :d="`M${-eye.x - 6} ${eye.y + 1}q6-8 12 0M${eye.x - 6} ${eye.y + 1}q6-8 12 0`" :stroke="eye.ink" stroke-width="3" fill="none" />
      <path v-else-if="beady" :d="`M${-eye.x - 7} ${eye.y - 6}l11 6-11 6M${eye.x + 7} ${eye.y - 6}l-11 6 11 6`" :stroke="eye.ink" stroke-width="3" fill="none" />
      <g v-else-if="mood === 'neutral' || mood === 'shy'">
        <ellipse cx="-16" cy="-8" rx="8" ry="7" fill="#fff" stroke-width="2.5" /><ellipse cx="16" cy="-8" rx="8" ry="7" fill="#fff" stroke-width="2.5" />
        <circle :cx="mood === 'shy' ? -12 : -15" cy="-5" r="3.2" :fill="OUTLINE" stroke="none" /><circle :cx="mood === 'shy' ? 20 : 17" cy="-5" r="3.2" :fill="OUTLINE" stroke="none" />
        <path v-if="mood === 'neutral'" d="M-24-8a8 7 0 0 1 16 0ZM8-8a8 7 0 0 1 16 0Z" :fill="c.body" stroke-width="2.5" />
      </g>
      <path v-else-if="mood === 'happy'" d="M-23-6q7-9 14 0M9-6q7-9 14 0" stroke-width="3" fill="none" />
      <path v-else d="M-24-14l12 6-12 6M24-14l-12 6 12 6" stroke-width="3" fill="none" />

      <!-- Mouth -->
      <template v-if="openMouth">
        <path :d="species === 'cat' ? 'M-8 10q8 13 16 0Z' : species === 'hamster' ? 'M-6 9q6 10 12 0Z' : 'M-7 14q7 11 14 0Z'" fill="#8A3B33" stroke-width="2.5" />
        <path v-if="species === 'hamster'" d="M-3 9.5h6v3.5h-6Z" fill="#fff" stroke-width="1.5" />
        <ellipse v-else :cy="species === 'cat' ? 16.5 : 19.5" rx="4" ry="2.8" fill="#F28B8B" stroke="none" />
      </template>
      <path v-else-if="species === 'cat'" :d="mood === 'shy' ? 'M-5 13q2.5-2 5 0t5 0' : 'M-8 11q4 4 8 0 4 4 8 0'" stroke-width="2.5" fill="none" />
      <path v-else-if="species === 'hamster'" :d="mood === 'shy' ? 'M-4 10q2-2 4 0t4 0' : 'M0 5v3M-6 8q3 4 6 0 3 4 6 0'" stroke-width="2.3" fill="none" />
      <path v-else :d="mood === 'shy' ? 'M-4 16q2-2 4 0t4 0' : 'M0 8v5M-7 13q3.5 4 7 0 3.5 4 7 0'" stroke-width="2.5" fill="none" />
    </g>
  </svg>
</template>
