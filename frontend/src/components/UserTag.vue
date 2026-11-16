<script setup>
import { ref } from 'vue'
import { Copy, Check } from 'lucide-vue-next'
const props = defineProps({ tag: { type: String, required: true } })
const copied = ref(false)
let timer
async function copy() {
  try {
    await navigator.clipboard.writeText(props.tag)
  } catch {
    // navigator.clipboard is unavailable outside secure contexts (e.g. plain http on a LAN IP).
    const input = Object.assign(document.createElement('textarea'), { value: props.tag })
    document.body.append(input); input.select(); document.execCommand('copy'); input.remove()
  }
  copied.value = true
  clearTimeout(timer); timer = setTimeout(() => { copied.value = false }, 1500)
}
</script>

<template>
  <span class="user-tag"><span>{{ tag }}</span><button type="button" class="icon-button" @click="copy" :aria-label="copied ? 'Đã sao chép' : 'Sao chép mã'" :title="copied ? 'Đã sao chép' : 'Sao chép mã'"><Check v-if="copied" :size="16"/><Copy v-else :size="16"/></button></span>
</template>
