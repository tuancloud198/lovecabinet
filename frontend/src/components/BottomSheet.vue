<script setup>
import { X } from 'lucide-vue-next'
defineProps({ title: String })
const emit = defineEmits(['close'])
</script>

<template>
  <div class="sheet-backdrop" @click.self="emit('close')">
    <section class="sheet" role="dialog" aria-modal="true" :aria-label="title">
      <header class="sheet-header"><h2>{{ title }}</h2><button class="icon-button" aria-label="Đóng" @click="emit('close')"><X :size="20" /></button></header>
      <slot />
    </section>
  </div>
</template>
