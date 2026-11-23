<script setup>
// A user's picture: their own photo (avatar_url, private, fetched with the token) or the dog
// character for their gender. The character shows while the photo loads or if it can't.
import { ref, computed, watch } from 'vue'
import { Check } from 'lucide-vue-next'
import { art, characterOf } from '@/characters.js'
import { photoSrc } from '@/photos.js'
const props = defineProps({ user: Object, mood: { type: String, default: 'neutral' }, size: { type: Number, default: 64 }, selected: Boolean })
const kind = computed(() => characterOf(props.user))
const photo = ref('')
watch(() => props.user?.avatar_url, async url => {
  photo.value = ''
  const src = url ? await photoSrc(url) : ''
  if (url === props.user?.avatar_url) photo.value = src
}, { immediate: true })
</script>

<template>
  <span class="character-avatar" :class="[kind, { photo }]" :style="{ width: size + 'px', height: size + 'px' }">
    <img :src="photo || art[`${kind}-${mood}`]" alt="" />
    <span v-if="selected" class="avatar-check"><Check :size="12" stroke-width="3" /></span>
  </span>
</template>
