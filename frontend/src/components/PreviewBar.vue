<script setup>
// Shown while trying a shop item: stays above the bottom nav on every page.
import { computed } from 'vue'
import { Eye, X } from 'lucide-vue-next'
import { buy, stopPreview } from '@/shop.js'
import { state } from '@/store.js'
const item = computed(() => state.preview.item)
const owned = computed(() => state.shop?.items.find(i => i.id === item.value.id)?.owned)
const short = computed(() => Math.max(0, item.value.price - (state.shop?.balance ?? 0)))
</script>

<template>
  <div class="preview-bar" role="status">
    <Eye :size="18" />
    <span class="preview-text"><strong>Đang xem thử</strong><small>{{ item.name }}</small></span>
    <button v-if="!owned" class="btn primary small" :disabled="state.busy || short > 0" @click="buy(item)">{{ short > 0 ? `Thiếu ${short} điểm` : `Mua · ${item.price}` }}</button>
    <button class="icon-button" aria-label="Thoát xem thử" @click="stopPreview"><X :size="18" /></button>
  </div>
</template>
