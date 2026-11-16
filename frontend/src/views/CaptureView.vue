<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { Amphora, Camera, ImagePlus, RefreshCw, X } from 'lucide-vue-next'
import { api } from '@/api.js'
import { isoDate } from '@/format.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import EmojiPicker from '@/components/EmojiPicker.vue'
import EmptyState from '@/components/EmptyState.vue'

const props = defineProps({ jarId: Number })
const jars = computed(() => [...state.jars].sort((a, b) => b.id - a.id))
const form = ref({ jar: props.jarId || jars.value[0]?.id, title: '', story: '', date: isoDate(), emoji: '❤️' })
const photos = ref([]) // [{ file, url }]
const current = ref(0)
const savedId = ref(null) // memory saved but some photos still pending

function pick(event) {
  for (const file of event.target.files) photos.value.push({ file, url: URL.createObjectURL(file) })
  current.value = Math.max(0, photos.value.length - 1)
  event.target.value = ''
}
function drop(index) {
  URL.revokeObjectURL(photos.value[index].url)
  photos.value.splice(index, 1)
  current.value = Math.min(current.value, Math.max(0, photos.value.length - 1))
}
onBeforeUnmount(() => photos.value.forEach(p => URL.revokeObjectURL(p.url)))

function save() {
  run(async () => {
    if (!savedId.value) savedId.value = (await api('memories/', { method: 'POST', body: form.value })).id
    while (photos.value.length) {
      const body = new FormData()
      body.append('memory', savedId.value)
      body.append('file', photos.value[0].file)
      await api('photos/', { method: 'POST', body })
      drop(0)
    }
    await load()
    toast('Đã lưu vào Tủ! ♡')
    state.owner = 'me'
    navigate('jar', { id: form.value.jar })
  })
}
</script>

<template>
  <div class="page">
    <AppHeader title="Lưu kỷ niệm" back @back="navigate('cabinet')">
      <label class="date-pill"><span class="visually-hidden">Ngày</span><input v-model="form.date" type="date" required :disabled="!!savedId" /></label>
    </AppHeader>

    <EmptyState v-if="!jars.length" title="Chưa có hũ nào" text="Tạo một chiếc hũ trong Tủ trước, rồi quay lại lưu kỷ niệm nhé!">
      <button class="btn primary" @click="navigate('cabinet')"><Amphora :size="18" /> Đến Tủ</button>
    </EmptyState>

    <form v-else class="capture" @submit.prevent="save">
      <div class="photo-frame">
        <template v-if="photos.length">
          <img :src="photos[current].url" alt="Ảnh đã chọn" />
          <label class="photo-action" aria-label="Chọn ảnh khác"><RefreshCw :size="18" /><input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="pick" /></label>
        </template>
        <div v-else class="photo-empty">
          <Camera :size="40" />
          <div class="photo-buttons">
            <label class="btn primary small"><Camera :size="16" /> Chụp ảnh<input type="file" accept="image/*" capture="environment" @change="pick" /></label>
            <label class="btn outline small"><ImagePlus :size="16" /> Thư viện<input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="pick" /></label>
          </div>
          <small>JPEG, PNG, WebP · tối đa 10 MB/ảnh</small>
        </div>
      </div>
      <div v-if="photos.length > 1" class="thumb-strip">
        <span v-for="(p, i) in photos" :key="p.url" class="thumb-wrap" :class="{ chosen: current === i }">
          <button type="button" :aria-label="`Ảnh ${i + 1}`" @click="current = i"><img :src="p.url" alt="" /></button>
          <button type="button" class="thumb-remove" aria-label="Bỏ ảnh" @click="drop(i)"><X :size="12" /></button>
        </span>
      </div>

      <section class="sheet-section stack">
        <div class="field"><span class="field-title">Chọn emoji cho kỷ niệm này</span><EmojiPicker v-model="form.emoji" /></div>
        <label class="field">Tên kỷ niệm<input v-model="form.title" required maxlength="150" placeholder="Buổi cà phê đầu tiên…" :disabled="!!savedId" /></label>
        <label class="field"><span class="label-text">Lời nhắn <span class="muted">(tùy chọn)</span></span>
          <textarea v-model="form.story" maxlength="200" rows="3" placeholder="Một buổi cà phê thật chill cùng nhau ♡" :disabled="!!savedId"></textarea>
          <span class="counter">{{ form.story.length }}/200</span>
        </label>
        <label class="field">Chọn hũ
          <select v-model="form.jar" required :disabled="!!savedId"><option v-for="j in jars" :key="j.id" :value="j.id">{{ j.emoji }} {{ j.name }}</option></select>
        </label>
        <p v-if="savedId" class="form-error">Kỷ niệm đã được lưu, còn {{ photos.length }} ảnh chưa tải lên. Bấm lưu để thử lại.</p>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy"><Amphora :size="18" /> {{ state.busy ? 'Đang lưu…' : 'Lưu vào Tủ' }}</button>
      </section>
    </form>
  </div>
</template>
