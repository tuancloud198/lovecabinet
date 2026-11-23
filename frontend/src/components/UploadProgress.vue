<script setup>
import { computed } from 'vue'
// "4/5 ảnh · 80%": `done` photos finished, `part` (0..1) of the current one sent.
const props = defineProps({ done: { type: Number, required: true }, total: { type: Number, required: true }, part: { type: Number, default: 0 } })
const percent = computed(() => Math.round(Math.min(1, (props.done + props.part) / props.total) * 100))
</script>

<template>
  <div class="upload-progress" role="progressbar" :aria-valuenow="percent" aria-valuemin="0" aria-valuemax="100" :aria-label="`Đã tải ${done}/${total} ảnh/video`">
    <div class="upload-progress-label"><span>Đã tải {{ done }}/{{ total }} ảnh/video</span><span>{{ percent }}%</span></div>
    <div class="upload-progress-track"><div class="upload-progress-bar" :style="{ width: `${percent}%` }"></div></div>
  </div>
</template>
