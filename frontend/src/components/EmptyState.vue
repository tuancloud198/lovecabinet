<script setup>
import { art } from '@/characters.js'
defineProps({ title: String, text: String })
</script>

<template>
  <div class="empty-state">
    <img :src="art['empty-box']" alt="" />
    <div><h3>{{ title }}</h3><p>{{ text }}</p><slot /></div>
  </div>
</template>
