<script setup>
import { computed } from 'vue'
import { CalendarDays, Amphora, Camera, Dog, Puzzle, ShoppingBag, UserRound } from 'lucide-vue-next'
import { state } from '@/store.js'
defineProps({ active: String })
defineEmits(['go'])
const tabs = [
  { name: 'calendar', label: 'Lịch', icon: CalendarDays },
  { name: 'cabinet', label: 'Tủ', icon: Amphora },
  { name: 'quiz', label: 'Đố vui', icon: Puzzle },
  { name: 'capture', label: 'Camera', icon: Camera, center: true }, // the middle of 7
  { name: 'pet', label: 'Nhân Vật', icon: Dog },
  { name: 'shop', label: 'Cửa hàng', icon: ShoppingBag },
  { name: 'profile', label: 'Hồ Sơ', icon: UserRound },
]
// Đố vui gets a dot while the partner has questions waiting for me.
const quizWaiting = computed(() => state.quiz.some(q => q.author !== state.me?.id && !q.answer))
</script>

<template>
  <nav class="bottom-nav" :class="{ locked: state.preview }" aria-label="Điều hướng chính">
    <button v-for="tab in tabs" :key="tab.name" :class="{ active: active === tab.name, center: tab.center }" :aria-current="active === tab.name ? 'page' : undefined" @click="$emit('go', tab.name)">
      <span class="nav-icon"><component :is="tab.icon" :size="tab.center ? 26 : 22" /><span v-if="tab.name === 'quiz' && quizWaiting" class="nav-dot" aria-label="Có câu đố mới"></span></span>
      <span v-if="!tab.center" class="nav-label">{{ tab.label }}</span>
      <span v-else class="visually-hidden">{{ tab.label }}</span>
    </button>
  </nav>
</template>
