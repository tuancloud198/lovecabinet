<script setup>
import { ChevronLeft } from 'lucide-vue-next'
defineProps({ title: String, subtitle: String, back: Boolean })
defineEmits(['back'])
</script>

<template>
  <header class="app-header">
    <button v-if="back" class="icon-button header-side" aria-label="Quay lại" @click="$emit('back')"><ChevronLeft :size="24" /></button>
    <span v-else class="header-side"></span>
    <div class="header-title">
      <h1>{{ title }}<slot name="title-suffix" /></h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div class="header-side header-actions"><slot /></div>
  </header>
</template>
