<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { X } from 'lucide-vue-next'
import { state, navigate, run, load, refresh } from '@/store.js'
import BottomNav from '@/components/BottomNav.vue'
import CabinetView from '@/views/CabinetView.vue'
import CalendarView from '@/views/CalendarView.vue'
import CaptureView from '@/views/CaptureView.vue'
import JarView from '@/views/JarView.vue'
import MemoryView from '@/views/MemoryView.vue'
import PairingView from '@/views/PairingView.vue'
import PetView from '@/views/PetView.vue'
import ProfileSetupView from '@/views/ProfileSetupView.vue'
import ProfileView from '@/views/ProfileView.vue'
import WelcomeView from '@/views/WelcomeView.vue'

const views = { cabinet: CabinetView, calendar: CalendarView, capture: CaptureView, jar: JarView, memory: MemoryView, pet: PetView, profile: ProfileView }
const TABS = ['calendar', 'cabinet', 'pet', 'profile']
const showNav = computed(() => TABS.includes(state.view.name))
const viewKey = computed(() => state.view.name + JSON.stringify(state.view.params))

// Coming back to the app (switching tabs, unlocking the phone): pick up what the partner added.
function onVisibility() { if (document.visibilityState === 'visible') refresh() }
onMounted(() => {
  if (state.token) run(load)
  document.addEventListener('visibilitychange', onVisibility)
})
onBeforeUnmount(() => document.removeEventListener('visibilitychange', onVisibility))
</script>

<template>
  <div class="phone">
    <WelcomeView v-if="!state.token" />
    <div v-else-if="!state.me" class="screen center-screen"><p class="muted" role="status">{{ state.busy ? 'Đang mở Tủ Thương…' : state.error }}</p></div>
    <ProfileSetupView v-else-if="state.onboarding === 'profile'" />
    <PairingView v-else-if="!state.couple || state.justPaired" />
    <template v-else>
      <main :class="{ 'with-nav': showNav }">
        <component :is="views[state.view.name]" :key="viewKey" v-bind="state.view.params" />
      </main>
      <BottomNav v-if="showNav" :active="state.view.name" @go="navigate" />
    </template>

    <div v-if="state.toast" class="toast" role="status">{{ state.toast }}</div>
    <div v-if="state.error && state.me && state.couple && !state.busy" class="toast error" role="alert">
      {{ state.error }}<button class="icon-button" aria-label="Đóng" @click="state.error = ''"><X :size="16" /></button>
    </div>
  </div>
</template>
