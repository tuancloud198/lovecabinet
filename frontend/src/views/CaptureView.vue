<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { Amphora, Camera, ImagePlus, MapPin, Play, X } from 'lucide-vue-next'
import { api, upload } from '@/api.js'
import { isoDate } from '@/format.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import EmojiPicker from '@/components/EmojiPicker.vue'
import EmptyState from '@/components/EmptyState.vue'
import PhotoViewer from '@/components/PhotoViewer.vue'
import UploadProgress from '@/components/UploadProgress.vue'
import LocationPicker from '@/components/LocationPicker.vue'
import { photoLocation, placeName } from '@/location.js'
import { isVideoFile, uploadablePhoto } from '@/photos.js'

const props = defineProps({ jarId: Number })
const jars = computed(() => [...state.jars].sort((a, b) => b.id - a.id))
const form = ref({ jar: props.jarId || jars.value[0]?.id, title: '', story: '', date: isoDate(), emoji: '❤️' })
const photos = ref([]) // [{ file, url, video, token? }]; token = already uploaded (staged)
const images = computed(() => photos.value.filter(p => !p.video)) // the viewer shows photos only
const current = ref(0)
const viewing = ref(false)
const progress = ref(null) // { done, total, part } while uploading

// Where it happened. The GPS of the first photo that has one comes first; once the location is
// set or removed by hand, picking more photos no longer changes it.
const location = ref(null) // { latitude, longitude, place }
const locationSource = ref('') // '' | 'photo' | 'manual'
const readingGps = ref(false)
const editingLocation = ref(false)
let locateRun = 0
async function locateFromPhotos() {
  if (locationSource.value === 'manual') return
  const id = ++locateRun
  readingGps.value = true
  for (const p of photos.value) if (!p.video && p.gps === undefined) p.gps = await photoLocation(p.file)
  if (id !== locateRun || locationSource.value === 'manual') return
  readingGps.value = false
  const found = photos.value.find(p => p.gps)?.gps
  if (!found) {
    if (locationSource.value === 'photo') { location.value = null; locationSource.value = '' }
    return
  }
  if (location.value?.latitude === found.latitude && location.value?.longitude === found.longitude) return
  location.value = { ...found, place: '' }
  locationSource.value = 'photo'
  const place = await placeName(found)
  if (location.value?.latitude === found.latitude && location.value?.longitude === found.longitude) location.value.place = place
}
function setLocation(value) {
  location.value = value
  locationSource.value = 'manual'
  editingLocation.value = false
  readingGps.value = false
}
const locationLabel = computed(() => {
  if (location.value) return location.value.place || 'Đã ghim vị trí'
  return readingGps.value ? 'Đang đọc vị trí từ ảnh…' : 'Chưa có địa điểm'
})

function pick(event) {
  for (const file of event.target.files) photos.value.push({ file, url: URL.createObjectURL(file), video: isVideoFile(file) })
  current.value = Math.max(0, photos.value.length - 1)
  event.target.value = ''
  locateFromPhotos()
}
function drop(index) {
  URL.revokeObjectURL(photos.value[index].url)
  photos.value.splice(index, 1)
  current.value = Math.min(current.value, Math.max(0, photos.value.length - 1))
  locateFromPhotos()
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
    await api('memories/', { method: 'POST', body: { ...form.value, ...(location.value ?? {}), staged_photos: photos.value.map(p => p.token) } })
    if (total) await new Promise(resolve => setTimeout(resolve, 700)) // let "5/5 · 100%" be seen
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
        <video v-if="photos.length && photos[current].video" :key="photos[current].url" class="photo-video" :src="photos[current].url" controls playsinline preload="metadata"></video>
        <button v-else-if="photos.length" type="button" class="photo-open" aria-label="Xem ảnh toàn màn hình" @click="viewing = true">
          <img v-if="!photos[current].noPreview" :src="photos[current].url" alt="Ảnh đã chọn" @error="photos[current].noPreview = true" />
          <span v-else class="photo-placeholder">📷</span> <!-- e.g. HEIC outside Safari: uploads fine, the server converts it -->
        </button>
        <div v-else class="photo-empty">
          <Camera :size="40" />
          <div class="photo-buttons">
            <label class="btn primary small"><Camera :size="16" /> Chụp / quay<input type="file" accept="image/*,video/*" capture="environment" @change="pick" /></label>
            <label class="btn outline small"><ImagePlus :size="16" /> Thư viện<input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif,video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm" multiple @change="pick" /></label>
          </div>
          <small>Ảnh JPEG, PNG, WebP, HEIC · tối đa 80 MB<br />Video MP4, MOV, WebM · tối đa 200 MB</small>
        </div>
      </div>
      <div v-if="photos.length" class="thumb-strip">
        <span v-for="(p, i) in photos" :key="p.url" class="thumb-wrap" :class="{ chosen: current === i }">
          <button type="button" :aria-label="p.video ? `Video ${i + 1}` : `Ảnh ${i + 1}`" @click="current = i">
            <span v-if="p.video" class="thumb-video"><video :src="`${p.url}#t=0.1`" muted playsinline preload="metadata"></video><Play :size="16" fill="currentColor" /></span>
            <img v-else-if="!p.noPreview" :src="p.url" alt="" @error="p.noPreview = true" /><span v-else class="photo-placeholder">📷</span>
          </button>
          <button type="button" class="thumb-remove" :aria-label="p.video ? 'Bỏ video' : 'Bỏ ảnh'" @click="drop(i)"><X :size="12" /></button>
        </span>
        <label class="thumb-add" aria-label="Thêm ảnh hoặc video từ thư viện"><ImagePlus :size="20" /><input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif,video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm" multiple @change="pick" /></label>
        <label class="thumb-add" aria-label="Chụp thêm ảnh hoặc quay video"><Camera :size="20" /><input type="file" accept="image/*,video/*" capture="environment" @change="pick" /></label>
      </div>
      <PhotoViewer v-if="viewing && images.length" :urls="images.map(p => p.url)" :start="Math.max(0, images.indexOf(photos[current]))" @close="viewing = false" />

      <section class="sheet-section stack">
        <div class="field"><span class="field-title">Chọn emoji cho kỷ niệm này</span><EmojiPicker v-model="form.emoji" /></div>
        <label class="field">Tên kỷ niệm<input v-model="form.title" required maxlength="150" placeholder="Buổi cà phê đầu tiên…" /></label>
        <label class="field"><span class="label-text">Lời nhắn <span class="muted">(tùy chọn)</span></span>
          <textarea v-model="form.story" maxlength="200" rows="3" placeholder="Một buổi cà phê thật chill cùng nhau ♡"></textarea>
          <span class="counter">{{ form.story.length }}/200</span>
        </label>
        <div class="field"><span>Địa điểm</span>
          <div class="location-row">
            <MapPin :size="18" class="location-icon" />
            <span class="location-text">{{ locationLabel }}<small v-if="locationSource === 'photo'" class="muted"> · từ ảnh</small></span>
            <button type="button" class="chip soft" @click="editingLocation = true">{{ location ? 'Sửa' : 'Thêm' }}</button>
            <button v-if="location" type="button" class="icon-button" aria-label="Bỏ địa điểm" @click="setLocation(null)"><X :size="16" /></button>
          </div>
        </div>
        <label class="field">Chọn hũ
          <select v-model="form.jar" required><option v-for="j in jars" :key="j.id" :value="j.id">{{ j.emoji }} {{ j.name }}</option></select>
        </label>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy"><Amphora :size="18" /> {{ state.busy ? 'Đang lưu…' : 'Lưu vào Tủ' }}</button>
        <UploadProgress v-if="state.busy && progress?.total" v-bind="progress" />
      </section>
    </form>
    <LocationPicker v-if="editingLocation" :location="location" @save="setLocation" @close="editingLocation = false" />
  </div>
</template>
