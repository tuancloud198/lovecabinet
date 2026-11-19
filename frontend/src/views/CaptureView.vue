<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { Amphora, Camera, ImagePlus, X } from 'lucide-vue-next'
import { api, upload } from '@/api.js'
import { isoDate } from '@/format.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import EmojiPicker from '@/components/EmojiPicker.vue'
import EmptyState from '@/components/EmptyState.vue'
import PhotoViewer from '@/components/PhotoViewer.vue'
import UploadProgress from '@/components/UploadProgress.vue'
import { uploadablePhoto } from '@/photos.js'

const props = defineProps({ jarId: Number })
const jars = computed(() => [...state.jars].sort((a, b) => b.id - a.id))
const form = ref({ jar: props.jarId || jars.value[0]?.id, title: '', story: '', date: isoDate(), emoji: '❤️' })
const photos = ref([]) // [{ file, url, token? }]; token = already uploaded (staged)
const current = ref(0)
const viewing = ref(false)
const progress = ref(null) // { done, total, part } while uploading

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

// Upload every photo first (staged), then create the memory with all of them in one
// request, so a failed upload never leaves a memory with missing photos. Already
// uploaded photos keep their token, so a retry only sends the rest.
function save() {
  run(async () => {
    const total = photos.value.length
    progress.value = { done: photos.value.filter(p => p.token).length, total, part: 0 }
    for (const p of photos.value) {
      if (p.token) continue
      const body = new FormData()
      body.append('file', await uploadablePhoto(p.file))
      p.token = (await upload('photos/stage/', body, part => { progress.value.part = part })).token
      progress.value = { ...progress.value, done: progress.value.done + 1, part: 0 }
    }
    await api('memories/', { method: 'POST', body: { ...form.value, staged_photos: photos.value.map(p => p.token) } })
    photos.value.forEach(p => URL.revokeObjectURL(p.url))
    photos.value = []
    await load()
    toast('Đã lưu vào Tủ! ♡')
    navigate('jar', { id: form.value.jar })
  })
}
</script>

<template>
  <div class="page">
    <AppHeader title="Lưu kỷ niệm" back @back="navigate('cabinet')">
      <label class="date-pill"><span class="visually-hidden">Ngày</span><input v-model="form.date" type="date" required /></label>
    </AppHeader>

    <EmptyState v-if="!jars.length" title="Chưa có hũ nào" text="Tạo một chiếc hũ trong Tủ trước, rồi quay lại lưu kỷ niệm nhé!">
      <button class="btn primary" @click="navigate('cabinet')"><Amphora :size="18" /> Đến Tủ</button>
    </EmptyState>

    <form v-else class="capture" @submit.prevent="save">
      <div class="photo-frame">
        <button v-if="photos.length" type="button" class="photo-open" aria-label="Xem ảnh toàn màn hình" @click="viewing = true">
          <img v-if="!photos[current].noPreview" :src="photos[current].url" alt="Ảnh đã chọn" @error="photos[current].noPreview = true" />
          <span v-else class="photo-placeholder">📷</span> <!-- e.g. HEIC outside Safari: uploads fine, the server converts it -->
        </button>
        <div v-else class="photo-empty">
          <Camera :size="40" />
          <div class="photo-buttons">
            <label class="btn primary small"><Camera :size="16" /> Chụp ảnh<input type="file" accept="image/*" capture="environment" @change="pick" /></label>
            <label class="btn outline small"><ImagePlus :size="16" /> Thư viện<input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif" multiple @change="pick" /></label>
          </div>
          <small>JPEG, PNG, WebP, HEIC · tối đa 80 MB/ảnh</small>
        </div>
      </div>
      <div v-if="photos.length" class="thumb-strip">
        <span v-for="(p, i) in photos" :key="p.url" class="thumb-wrap" :class="{ chosen: current === i }">
          <button type="button" :aria-label="`Ảnh ${i + 1}`" @click="current = i"><img v-if="!p.noPreview" :src="p.url" alt="" @error="p.noPreview = true" /><span v-else class="photo-placeholder">📷</span></button>
          <button type="button" class="thumb-remove" aria-label="Bỏ ảnh" @click="drop(i)"><X :size="12" /></button>
        </span>
        <label class="thumb-add" aria-label="Thêm ảnh từ thư viện"><ImagePlus :size="20" /><input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif" multiple @change="pick" /></label>
        <label class="thumb-add" aria-label="Chụp thêm ảnh"><Camera :size="20" /><input type="file" accept="image/*" capture="environment" @change="pick" /></label>
      </div>
      <PhotoViewer v-if="viewing && photos.length" :urls="photos.map(p => p.url)" :start="current" @close="viewing = false" />

      <section class="sheet-section stack">
        <div class="field"><span class="field-title">Chọn emoji cho kỷ niệm này</span><EmojiPicker v-model="form.emoji" /></div>
        <label class="field">Tên kỷ niệm<input v-model="form.title" required maxlength="150" placeholder="Buổi cà phê đầu tiên…" /></label>
        <label class="field"><span class="label-text">Lời nhắn <span class="muted">(tùy chọn)</span></span>
          <textarea v-model="form.story" maxlength="200" rows="3" placeholder="Một buổi cà phê thật chill cùng nhau ♡"></textarea>
          <span class="counter">{{ form.story.length }}/200</span>
        </label>
        <label class="field">Chọn hũ
          <select v-model="form.jar" required><option v-for="j in jars" :key="j.id" :value="j.id">{{ j.emoji }} {{ j.name }}</option></select>
        </label>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy"><Amphora :size="18" /> {{ state.busy ? 'Đang lưu…' : 'Lưu vào Tủ' }}</button>
        <UploadProgress v-if="state.busy && progress?.total" v-bind="progress" />
      </section>
    </form>
  </div>
</template>
