<script setup>
import { CalendarDays, Amphora, Camera, Dog, UserRound } from 'lucide-vue-next'
defineProps({ active: String })
defineEmits(['go'])
const tabs = [
  { name: 'calendar', label: 'Lịch', icon: CalendarDays },
  { name: 'cabinet', label: 'Tủ', icon: Amphora },
  { name: 'capture', label: 'Camera', icon: Camera, center: true },
  { name: 'pet', label: 'Nhân Vật', icon: Dog },
  { name: 'profile', label: 'Hồ Sơ', icon: UserRound },
]
</script>

<template>
  <nav class="bottom-nav" aria-label="Điều hướng chính">
    <button v-for="tab in tabs" :key="tab.name" :class="{ active: active === tab.name, center: tab.center }" :aria-current="active === tab.name ? 'page' : undefined" @click="$emit('go', tab.name)">
      <span class="nav-icon"><component :is="tab.icon" :size="tab.center ? 26 : 22" /></span>
      <span v-if="!tab.center" class="nav-label">{{ tab.label }}</span>
      <span v-else class="visually-hidden">{{ tab.label }}</span>
    </button>
  </nav>
</template>
