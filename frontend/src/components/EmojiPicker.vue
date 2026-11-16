<script setup>
import { ref } from 'vue'
import { Ellipsis } from 'lucide-vue-next'
const model = defineModel({ type: String })
const props = defineProps({ quick: { type: Number, default: 6 } })
// Same set as the design system's "Chọn emoji" grid.
const emojis = ['❤️', '🎂', '☕', '🌷', '🎁', '😍', '🥰', '😀', '✈️', '🌲', '📷', '🎬', '🍮', '🍕', '🎮', '✨']
const expanded = ref(false)
</script>

<template>
  <div class="emoji-picker" role="radiogroup" aria-label="Chọn emoji">
    <button v-for="emoji in expanded ? emojis : emojis.slice(0, props.quick)" :key="emoji" type="button" role="radio" :aria-checked="model === emoji" :class="{ chosen: model === emoji }" @click="model = emoji">{{ emoji }}</button>
    <button v-if="!expanded" type="button" class="more" aria-label="Thêm emoji" @click="expanded = true"><Ellipsis :size="18" /></button>
  </div>
</template>
