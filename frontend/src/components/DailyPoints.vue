<script setup>
// Today's points towards the couple's daily limit (memories + quiz answers, resets at midnight).
import { computed } from 'vue'
import { Sparkles } from 'lucide-vue-next'
import { state } from '@/store.js'
const today = computed(() => state.couple?.points_today || 0)
const limit = computed(() => state.couple?.daily_points_limit || 100)
const full = computed(() => today.value >= limit.value)
</script>

<template>
  <div class="daily-points" :class="{ full }">
    <div class="daily-points-head">
      <span class="daily-points-icon"><Sparkles :size="16" /></span>
      <span class="daily-points-text">
        <strong>Điểm hôm nay: {{ today }}/{{ limit }}</strong>
        <small>{{ full ? 'Đủ điểm hôm nay rồi, mai quay lại nuôi bạn nhỏ tiếp nhé ♡' : 'Kỷ niệm và câu đố cộng điểm tới khi đủ, mỗi ngày làm mới.' }}</small>
      </span>
    </div>
    <div class="daily-points-track" role="progressbar" :aria-valuenow="today" aria-valuemin="0" :aria-valuemax="limit" aria-label="Điểm hôm nay">
      <span :style="{ width: Math.min(100, (today / limit) * 100) + '%' }"></span>
    </div>
  </div>
</template>
