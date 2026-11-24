<script setup>
import { computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { X } from 'lucide-vue-next'
import { state, navigate, run, load, refresh, toast } from '@/store.js'
import BottomNav from '@/components/BottomNav.vue'
import PreviewBar from '@/components/PreviewBar.vue'
import CabinetView from '@/views/CabinetView.vue'
import CalendarView from '@/views/CalendarView.vue'
import CaptureView from '@/views/CaptureView.vue'
import JarView from '@/views/JarView.vue'
import MapView from '@/views/MapView.vue'
import MemoryView from '@/views/MemoryView.vue'
import PairingView from '@/views/PairingView.vue'
import PetView from '@/views/PetView.vue'
import ProfileSetupView from '@/views/ProfileSetupView.vue'
import ProfileView from '@/views/ProfileView.vue'
import QuizView from '@/views/QuizView.vue'
import ShopView from '@/views/ShopView.vue'
import WelcomeView from '@/views/WelcomeView.vue'

const views = { cabinet: CabinetView, calendar: CalendarView, capture: CaptureView, jar: JarView, map: MapView, memory: MemoryView, pet: PetView, profile: ProfileView, quiz: QuizView, shop: ShopView }
const TABS = ['calendar', 'cabinet', 'quiz', 'pet', 'shop', 'profile']
const showNav = computed(() => TABS.includes(state.view.name))
const viewKey = computed(() => state.view.name + JSON.stringify(state.view.params))

// Each partner's own look (a theme bought in the shop, or one being tried): <html data-theme="pink">.
watch(() => (state.preview ? state.preview.theme : state.me?.theme), theme => {
  if (theme) document.documentElement.dataset.theme = theme
  else delete document.documentElement.dataset.theme
}, { immediate: true })

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
      <!-- Look-only while trying a shop item: the page can't be tapped (scrolling still works). -->
      <div v-if="state.preview" class="look-only" aria-hidden="true" @click="toast('Đang xem thử: chỉ xem thôi nhé')"></div>
      <PreviewBar v-if="state.preview" />
      <BottomNav v-if="showNav" :active="state.view.name" @go="navigate" />
    </template>

    <div v-if="state.toast" class="toast" role="status">{{ state.toast }}</div>
    <div v-if="state.error && state.me && state.couple && !state.busy" class="toast error" role="alert">
      {{ state.error }}<button class="icon-button" aria-label="Đóng" @click="state.error = ''"><X :size="16" /></button>
    </div>
  </div>
</template>
