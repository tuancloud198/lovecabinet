<script setup>
import { computed } from 'vue'
import { Check } from 'lucide-vue-next'
import { art, characterOf } from '@/characters.js'
const props = defineProps({ user: Object, mood: { type: String, default: 'neutral' }, size: { type: Number, default: 64 }, selected: Boolean })
const kind = computed(() => characterOf(props.user))
</script>

<template>
  <span class="character-avatar" :class="kind" :style="{ width: size + 'px', height: size + 'px' }">
    <img :src="art[`${kind}-${mood}`]" alt="" />
    <span v-if="selected" class="avatar-check"><Check :size="12" stroke-width="3" /></span>
  </span>
</template>
