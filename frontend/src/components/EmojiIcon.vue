<script setup>
import { computed } from 'vue'
import { emojiImage } from '@/emoji.js'
// An emoji as artwork (emoji.js); unknown ones fall back to the text glyph. Sized by font-size (1em).
const props = defineProps({ emoji: { type: String, default: '' } })
const src = computed(() => emojiImage(props.emoji))
</script>

<template>
  <img v-if="src" class="emoji-icon" :src="src" :alt="emoji" draggable="false" />
  <span v-else class="emoji-icon emoji-text">{{ emoji }}</span>
</template>
