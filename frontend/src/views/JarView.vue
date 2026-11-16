<script setup>
import { computed } from 'vue'
import { ChevronRight, Camera, Trash2 } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate } from '@/format.js'
import { state, partner, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import JarArt from '@/components/JarArt.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'

const props = defineProps({ id: Number })
const jar = computed(() => state.jars.find(j => j.id === props.id))
const ownerId = computed(() => (state.owner === 'me' ? state.me.id : partner.value?.id))
const memories = computed(() => state.memories.filter(m => m.jar === props.id && m.author === ownerId.value).sort((a, b) => b.date.localeCompare(a.date)))

function removeJar() {
  if (!window.confirm(`Xóa hũ "${jar.value.name}" và tất cả kỷ niệm bên trong?`)) return
  run(async () => {
    await api(`jars/${props.id}/`, { method: 'DELETE' })
    navigate('cabinet')
    await load()
    toast('Đã xóa hũ.')
  })
}
</script>

<template>
  <div v-if="jar" class="page">
    <AppHeader :title="jar.name" :subtitle="`${memories.length} kỷ niệm`" back @back="navigate('cabinet')">
      <button class="icon-button" aria-label="Xóa hũ" @click="removeJar"><Trash2 :size="20" /></button>
    </AppHeader>
    <div class="jar-stage">
      <JarArt :color="jar.color" :emojis="memories.length ? memories.map(m => m.emoji) : [jar.emoji]" large />
    </div>
    <section class="sheet-section">
      <div class="section-head"><h2>Các kỷ niệm trong hũ ({{ memories.length }})</h2><button v-if="state.owner === 'me'" class="btn small primary" @click="navigate('capture', { jarId: jar.id })"><Camera :size="16" /> Thêm</button></div>
      <EmptyState v-if="!memories.length" title="Chưa có kỷ niệm nào" :text="state.owner === 'me' ? 'Hãy chụp một bức ảnh để lưu giữ khoảnh khắc đầu tiên cùng nhau nhé! ♡' : 'Người ấy chưa lưu kỷ niệm nào vào hũ này.'">
        <button v-if="state.owner === 'me'" class="btn primary" @click="navigate('capture', { jarId: jar.id })"><Camera :size="18" /> Chụp ngay</button>
      </EmptyState>
      <button v-for="m in memories" :key="m.id" class="memory-row card" @click="navigate('memory', { id: m.id })">
        <span class="thumb"><PrivatePhoto v-if="m.photos[0]" :url="m.photos[0].url" /><span v-else>{{ m.emoji }}</span></span>
        <span class="row-text"><small class="date">{{ m.emoji }} {{ displayDate(m.date) }}</small><strong>{{ m.title }}</strong><small class="clamp">{{ m.story }}</small></span>
        <ChevronRight :size="20" />
      </button>
    </section>
  </div>
</template>
