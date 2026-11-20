<script setup>
// The couple's pet. Hand-drawn art is used when it exists in src/assets/characters, named
//   <species>-1|2|3 (growth stages, full body) and <species>-neutral|happy|shy|excited (faces),
// e.g. capybara-2.webp, capybara-happy.webp (the dog's files are male-*). Transparent background,
// drawn like task/ui-source/Dog-Growth.png. Until a species has its art, it is drawn below.
// The fallback drawings follow the dog's design: facing right in 3/4 view, sitting, big head,
// sleepy half-lidded eyes, smirk with the tongue out when happy, peach blush, thick dark outline,
// soft warm shading, an accessory on the head, a grass patch and yellow sparkle lines.
import { computed } from 'vue'
import { art } from '@/characters.js'

const props = defineProps({
  species: { type: String, default: 'dog' }, // dog | cat | capybara | honey_badger | hamster
  stage: { type: Number, default: 2 },       // 0 baby, 1 growing, 2 adult
  mood: { type: String, default: 'neutral' }, // neutral | happy | shy | excited
  face: Boolean,                              // head only (avatars, chips)
})

const INK = '#2E1F17'
const SPECIES = {
  cat: {
    fur: '#F8D3A0', light: '#FFF0D9', shade: '#E9B47A', mark: '#E39A57', belly: '#FFF3E2', paw: '#FFF3E2',
    eyes: { bx: -5, fx: 16, y: -7 }, mouth: { x: 30, y: 17 }, blush: { x: 16, y: 10 },
  },
  capybara: {
    fur: '#D49A64', light: '#E8BC8C', shade: '#B67B47', mark: '#9C6338', belly: '#E6BB8C', paw: '#A9703F',
    eyes: { bx: -9, fx: 12, y: -15 }, mouth: { x: 40, y: 20 }, blush: { x: 18, y: 4 },
  },
  honey_badger: {
    fur: '#5A5453', light: '#78716F', shade: '#423D3C', mark: '#ECE6DA', belly: '#6E6765', paw: '#3E3938',
    eyes: { bx: -7, fx: 14, y: -5 }, mouth: { x: 36, y: 16 }, blush: { x: 15, y: 9 },
  },
  hamster: {
    fur: '#F4C35C', light: '#FFE3A1', shade: '#E2A43E', mark: '#D68F2A', belly: '#FFF4DC', paw: '#F6B7A6',
    eyes: { bx: -6, fx: 15, y: -9 }, mouth: { x: 30, y: 13 }, blush: { x: 15, y: 7 },
  },
}
const s = computed(() => SPECIES[props.species] ?? SPECIES.cat)
const artFile = computed(() => {
  const prefix = props.species === 'dog' ? 'male' : props.species
  return art[props.face ? `${prefix}-${props.mood}` : `${prefix}-${props.stage + 1}`]
})
const id = computed(() => `pet-${props.species}`) // gradient ids (same species => same defs, safe to repeat)
const bodyScale = computed(() => [0.74, 0.87, 1][props.stage] ?? 1)
const headScale = computed(() => [0.92, 0.96, 1][props.stage] ?? 1)
// Body is drawn for an adult sitting on y = 152; the head sits on its shoulders.
const head = computed(() => {
  const drop = props.species === 'hamster' ? 10 : props.species === 'honey_badger' ? 8 : 0
  return { x: 100 + 8 * bodyScale.value, y: 152 - 92 * bodyScale.value + drop }
})
const sleepy = computed(() => props.mood === 'neutral' || props.mood === 'shy')
const openMouth = computed(() => props.mood === 'happy' || props.mood === 'excited')
const RX = 10
const RY = 8.5
// Upper half of an eye, filled with fur and edged with a heavy lid line (the dog's "chill" look).
const lid = x => `M${x - RX - 1} ${s.value.eyes.y}a${RX + 1} ${RY + 1} 0 0 1 ${2 * RX + 2} 0Z`
</script>

<template>
  <img v-if="artFile" class="pet-art" :src="artFile" alt="" />
  <svg v-else class="pet-art" :viewBox="face ? '-52 -64 126 108' : '26 0 164 166'" aria-hidden="true"
       :stroke="INK" stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round">
    <defs>
      <radialGradient :id="`${id}-fur`" cx="35%" cy="30%" r="80%">
        <stop offset="0" :stop-color="s.light" /><stop offset=".55" :stop-color="s.fur" /><stop offset="1" :stop-color="s.shade" />
      </radialGradient>
    </defs>

    <!-- Grass, body, legs and tail (full figure only) -->
    <g v-if="!face">
      <ellipse cx="104" cy="154" rx="70" ry="9" fill="#DCEDB8" stroke="none" />
      <path d="M44 154q1-9 5-13M50 155q1-6 4-9M158 154q-1-10-6-14M165 155q0-6-3-9M134 157q2-6 6-8" stroke="#93C462" stroke-width="3.2" fill="none" />
      <g :transform="`translate(100 152) scale(${bodyScale}) translate(-100 -152)`">
        <!-- tail, behind the body -->
        <template v-if="species === 'cat'">
          <path d="M66 140c-26 0-30-30-14-42" fill="none" :stroke="INK" stroke-width="15" />
          <path d="M66 140c-26 0-30-30-14-42" fill="none" :stroke="s.fur" stroke-width="8" />
          <path d="M53 104l4-5M50 112l6-3" :stroke="s.mark" stroke-width="3" fill="none" />
        </template>
        <path v-else-if="species === 'honey_badger'" d="M64 136c-14 2-22-6-20-16 6 2 12 4 22 6Z" :fill="s.fur" />

        <!-- sitting torso (hamster: a round ball) -->
        <ellipse v-if="species === 'hamster'" cx="100" cy="120" rx="44" ry="36" :fill="`url(#${id}-fur)`" />
        <path v-else-if="species === 'capybara'" d="M90 80c-30 6-42 36-38 72h90c4-30-6-60-30-70Z" :fill="`url(#${id}-fur)`" />
        <path v-else-if="species === 'honey_badger'" d="M92 86c-28 6-40 34-36 66h86c4-28-6-56-30-66Z" :fill="`url(#${id}-fur)`" />
        <path v-else d="M96 84c-22 8-36 34-32 68h70c4-26-2-52-16-66Z" :fill="`url(#${id}-fur)`" />

        <!-- belly / markings -->
        <path v-if="species === 'hamster'" d="M84 150c-10-16-6-36 14-40 22-2 32 16 24 40Z" :fill="s.belly" stroke="none" />
        <path v-else-if="species === 'capybara'" d="M106 152c-4-22 2-46 16-60 14 14 20 38 16 60Z" :fill="s.belly" stroke="none" />
        <path v-else-if="species === 'cat'" d="M104 152c-4-20 0-40 12-54 10 14 14 34 12 54Z" :fill="s.belly" stroke="none" />
        <template v-if="species === 'honey_badger'">
          <!-- silver cape along the top of the back -->
          <path d="M60 128c2-22 14-38 32-42l14 4c-16 8-28 20-34 40Z" :fill="s.mark" stroke="none" />
          <path d="M92 86c-28 6-40 34-36 66" fill="none" />
        </template>
        <template v-if="species === 'cat'">
          <path d="M70 118q8 2 10 9M68 132q8 1 10 7" :stroke="s.mark" stroke-width="3" fill="none" />
        </template>
        <template v-if="species === 'capybara'">
          <path d="M64 110q6-4 12-4M60 126q6-3 12-2" :stroke="s.mark" stroke-width="2.6" fill="none" />
        </template>

        <!-- back haunch and foot -->
        <ellipse v-if="species !== 'hamster'" cx="78" cy="136" rx="21" ry="16" :fill="s.fur" />
        <ellipse :cx="species === 'hamster' ? 82 : 74" cy="151" rx="13" ry="5.5" :fill="species === 'hamster' ? s.paw : s.fur" />

        <!-- front legs (hamster: paws holding a sunflower seed) -->
        <template v-if="species === 'hamster'">
          <path d="M108 112c8 4 9 16 0 22-8-6-7-18 0-22Z" fill="#4A4342" stroke-width="2.6" /><path d="M108 116v14" stroke="#E8E1D6" stroke-width="2" />
          <ellipse cx="98" cy="126" rx="7" ry="8" :fill="s.paw" /><ellipse cx="118" cy="124" rx="7" ry="8" :fill="s.paw" />
          <ellipse cx="118" cy="151" rx="13" ry="5.5" :fill="s.paw" />
        </template>
        <template v-else>
          <!-- rounded front legs with toes, like the dog's -->
          <path :d="`M104 ${species === 'capybara' ? 122 : 112}v24c0 6 3 8 8 8s8-2 8-8v-24`" :fill="s.fur" />
          <path :d="`M121 ${species === 'capybara' ? 120 : 110}v26c0 6 3 8 8 8s8-2 8-8v-26`" :fill="s.fur" />
          <path d="M109 150v3M114 150v3M126 150v3M131 150v3" stroke-width="2" />
          <path v-if="species === 'honey_badger'" d="M106 152l-1 4M111 152v4M116 152l1 4M121 152l-1 4M126 152v4M131 152l1 4M66 154l-1 3M72 155v3M78 154l1 3" :stroke="s.mark" stroke-width="2.2" />
        </template>
        <!-- honey badger's red bandana -->
        <path v-if="species === 'honey_badger'" d="M92 90c10 6 26 6 36-2l-4 12c-6 4-12 6-18 6l-6 10-4-12c-4-4-5-8-4-14Z" fill="#E0574E" stroke-width="2.8" />
      </g>
      <!-- sparkles for a happy pet, like the dog's -->
      <path v-if="mood === 'happy' || mood === 'excited'" :transform="`translate(${head.x - 108} ${head.y - 60})`"
            d="M150 18l6-9M160 28l9-5M144 10l1-9" stroke="#F5C12E" stroke-width="4.5" fill="none" />
    </g>

    <!-- Head, centred on (0, 0), facing right -->
    <g :transform="face ? '' : `translate(${head.x} ${head.y}) scale(${headScale})`">
      <template v-if="species === 'cat'">
        <path d="M-30-12-28-50-6-30Z" :fill="s.fur" />
        <path d="M2-30 22-54 32-16Z" :fill="s.fur" /><path d="M9-29 21-45 26-22Z" fill="#F6A9A3" stroke="none" />
        <ellipse rx="38" ry="31" :fill="`url(#${id}-fur)`" />
        <ellipse cx="30" cy="11" rx="17" ry="13" :fill="s.belly" stroke="none" />
        <path d="M-12-29q2 6 0 11M-4-31q2 7 0 12M4-30q2 6 0 10" :stroke="s.mark" stroke-width="3" fill="none" />
        <path d="M36 2h8l-4 5Z" fill="#E88A8A" stroke-width="2.2" />
        <path d="M44 12l14-3M44 17l13 2" stroke-width="1.8" fill="none" />
        <!-- pink bow on the back ear -->
        <g transform="translate(-22 -38) rotate(-18)"><path d="M0 0-12-7v14ZM0 0l12-7v14Z" fill="#F28FA0" stroke-width="2.2" /><circle r="3.6" fill="#E86F86" stroke-width="2.2" /></g>
      </template>

      <template v-else-if="species === 'capybara'">
        <ellipse cx="-24" cy="-33" rx="8" ry="6.5" :fill="s.shade" />
        <path d="M-38-6c0-20 12-30 36-30h28c18 0 30 10 32 24l2 18c1 14-9 24-24 24h-46c-18 0-28-12-28-36Z" :fill="`url(#${id}-fur)`" />
        <path d="M24 12c0-10 10-14 22-14 10 0 14 6 14 14s-6 18-18 18c-10 0-18-6-18-18Z" :fill="s.belly" stroke="none" />
        <!-- big blunt capybara nose -->
        <path d="M40-12c6-5 15-3 18 4 2 7-3 12-10 11-7-1-11-9-8-15Z" fill="#4E3020" stroke="none" />
        <ellipse cx="51" cy="-8" rx="2.4" ry="1.6" fill="#8A5F44" stroke="none" />
        <path d="M-14-32q4-4 9-4M2-36q3-3 6-3" :stroke="s.mark" stroke-width="2.4" fill="none" />
        <!-- the classic capybara mandarin -->
        <circle cx="0" cy="-44" r="10" fill="#F5A33B" /><path d="M0-54q8-9 15-4-6 9-15 4Z" fill="#7DB35A" stroke-width="2.2" />
        <circle cx="-3" cy="-47" r="2" fill="#FFD27F" stroke="none" />
      </template>

      <template v-else-if="species === 'honey_badger'">
        <ellipse cx="-24" cy="-24" rx="8" ry="7" :fill="s.fur" />
        <path d="M-38 2c0-24 18-34 42-32 22 2 38 14 50 28 4 6 2 12-6 14-12 4-22 12-42 14-26 2-44-6-44-24Z" :fill="`url(#${id}-fur)`" />
        <!-- silver-white cape from the forehead back, outline redrawn on top -->
        <path d="M-38 2c0-24 18-34 42-32 18 2 32 10 42 20-14-4-28-4-42 0-16 4-30 8-42 12Z" :fill="s.mark" stroke="none" />
        <path d="M-38 2c0-24 18-34 42-32 22 2 38 14 50 28 4 6 2 12-6 14-12 4-22 12-42 14-26 2-44-6-44-24Z" fill="none" />
        <ellipse cx="53" cy="0" rx="6.5" ry="5" fill="#141010" stroke="none" />
      </template>

      <template v-else>
        <circle cx="-22" cy="-27" r="10" :fill="s.fur" /><circle cx="-22" cy="-27" r="5" :fill="s.paw" stroke="none" />
        <circle cx="8" cy="-31" r="10" :fill="s.fur" /><circle cx="8" cy="-31" r="5" :fill="s.paw" stroke="none" />
        <ellipse rx="40" ry="33" :fill="`url(#${id}-fur)`" />
        <!-- cream face with a puffy cheek pouch -->
        <path d="M2 2c8-10 30-10 38 2 6 10 2 24-12 28-18 4-32-4-32-14 0-6 2-12 6-16Z" :fill="s.belly" stroke="none" />
        <path d="M-6-32q2 6 0 11M2-33q2 6 0 11" :stroke="s.mark" stroke-width="2.4" fill="none" />
        <ellipse cx="38" cy="2" rx="4.5" ry="3.4" fill="#EF8A8A" stroke-width="2" />
      </template>

      <!-- Blush (the dog's peach cheeks; diagonal strokes when shy) -->
      <ellipse :cx="s.blush.x" :cy="s.blush.y" rx="8" ry="5" fill="#F4A08C" opacity=".7" stroke="none" />
      <path v-if="mood === 'shy'" :transform="`translate(${s.blush.x} ${s.blush.y})`" d="M-8 3l4-6M-3 4l4-6M2 4l4-6" stroke="#E3685E" stroke-width="1.8" fill="none" />

      <!-- Eyes: two big whites close together, heavy sleepy lids -->
      <g v-if="sleepy">
        <ellipse :cx="s.eyes.bx" :cy="s.eyes.y" :rx="RX" :ry="RY" fill="#fff" stroke-width="3" />
        <ellipse :cx="s.eyes.fx" :cy="s.eyes.y" :rx="RX" :ry="RY" fill="#fff" stroke-width="3" />
        <circle :cx="s.eyes.bx + (mood === 'shy' ? 3.5 : 1.5)" :cy="s.eyes.y + 3" r="3.6" :fill="INK" stroke="none" />
        <circle :cx="s.eyes.fx + (mood === 'shy' ? 3.5 : 1.5)" :cy="s.eyes.y + 3" r="3.6" :fill="INK" stroke="none" />
        <path :d="lid(s.eyes.bx)" :fill="s.fur" stroke-width="3.4" /><path :d="lid(s.eyes.fx)" :fill="s.fur" stroke-width="3.4" />
      </g>
      <path v-else-if="mood === 'happy'" :d="`M${s.eyes.bx - 8} ${s.eyes.y + 2}q8-10 16 0M${s.eyes.fx - 8} ${s.eyes.y + 2}q8-10 16 0`"
            :stroke="species === 'honey_badger' ? '#F4EFE6' : INK" stroke-width="3.4" fill="none" />
      <path v-else :d="`M${s.eyes.bx - 7} ${s.eyes.y - 6}l11 6-11 6M${s.eyes.fx + 7} ${s.eyes.y - 6}l-11 6 11 6`"
            :stroke="species === 'honey_badger' ? '#F4EFE6' : INK" stroke-width="3.4" fill="none" />

      <!-- Mouth: the dog's smirk, tongue out when happy -->
      <g :transform="`translate(${s.mouth.x} ${s.mouth.y})`">
        <template v-if="openMouth">
          <path d="M-10-2q10 10 20-2Z" fill="#7E2F2A" stroke-width="2.8" />
          <path d="M-3 3c-1 9 2 14 7 14s7-6 5-15" fill="#F2899A" stroke-width="2.6" /><path d="M2 6v7" stroke="#D96478" stroke-width="1.8" />
        </template>
        <path v-else-if="mood === 'shy'" d="M-6 0q3-3 6 0t6 0" stroke-width="2.6" fill="none" />
        <path v-else d="M-10-1q9 7 18-3" stroke-width="2.8" fill="none" />
      </g>
    </g>
  </svg>
</template>
