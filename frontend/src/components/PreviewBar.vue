<script setup>
// Shown while trying a shop item: stays above the bottom nav on every page, counts down and ends the
// preview when time is up.
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Eye, X } from 'lucide-vue-next'
import { buy, stopPreview } from '@/shop.js'
import { state, toast } from '@/store.js'
const item = computed(() => state.preview.item)
const owned = computed(() => state.shop?.items.find(i => i.id === item.value.id)?.owned)
const short = computed(() => Math.max(0, item.value.price - (state.shop?.balance ?? 0)))
const left = ref(0)
let timer
function tick() {
  left.value = Math.max(0, Math.ceil((state.preview.endsAt - Date.now()) / 1000))
  if (!left.value) { stopPreview(); toast('Hết thời gian xem thử.') }
}
onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="preview-bar" role="status">
    <Eye :size="18" />
    <span class="preview-text"><strong>{{ item.name }}</strong><small>Chỉ xem · còn {{ left }}s</small></span>
    <button v-if="!owned" class="btn primary small" :disabled="state.busy || short > 0" @click="buy(item)">{{ short > 0 ? `Thiếu ${short} điểm` : `Mua · ${item.price}` }}</button>
    <button class="icon-button" aria-label="Thoát xem thử" @click="stopPreview()"><X :size="18" /></button>
  </div>
</template>
