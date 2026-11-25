<script setup>
// Shown while a photo/video loads: the couple's pet at its current stage, going blurry and clear.
// `still`: no animation (the media failed to load, or there's no preview).
import { computed } from 'vue'
import { petStatus } from '@/characters.js'
import { state } from '@/store.js'
import PetArt from '@/components/PetArt.vue'
defineProps({ still: Boolean })
const stage = computed(() => state.couple ? petStatus(state.memories || [], state.couple.points_earned || 0).stageIndex : 0)
</script>

<template>
  <span class="pet-loader" :class="{ still }" role="img" :aria-label="still ? 'Không tải được' : 'Đang tải…'"><PetArt :stage="stage" /></span>
</template>
