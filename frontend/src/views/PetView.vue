<script setup>
import { ref, computed } from 'vue'
import { ArrowRight, Pencil } from 'lucide-vue-next'
import { api } from '@/api.js'
import { MEMORY_POINTS, PETS, petStatus, QUIZ_POINTS, STAGES, stageLabel } from '@/characters.js'
import { state, navigate, run, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import PetArt from '@/components/PetArt.vue'

const pet = computed(() => petStatus(state.memories, state.couple.pet_points || 0))
const name = computed(() => state.couple.pet_name)
const species = computed(() => state.preview?.pet || state.couple.pet_type) // the pet shown (a shop preview, else ours)
const remaining = computed(() => pet.value.target - pet.value.count)

// The face on the big picture: picked by the couple (shared), or '' = follow the automatic mood below.
const MOOD_FACES = [
  { face: 'neutral', label: 'Bình thản' },
  { face: 'happy', label: 'Vui vẻ' },
  { face: 'shy', label: 'Ngại ngùng' },
  { face: 'excited', label: 'Phấn khích' },
]
// Only the moods this pet has a head for (the ragged dog has one face: no picker then).
const moodFaces = computed(() => MOOD_FACES.filter(m => (PETS[species.value] || PETS.dog).heads[m.face]))
const pickedMood = computed(() => state.couple.pet_mood || '')
const bigMood = computed(() => pickedMood.value || pet.value.mood.face)
function pickMood(pet_mood) {
  if (pet_mood === pickedMood.value) return
  run(async () => {
    Object.assign(state.couple, await api(`couples/${state.couple.id}/`, { method: 'PATCH', body: { pet_mood } }))
  })
}

const editing = ref(false)
const form = ref({})
function startEdit() {
  form.value = { pet_name: name.value }
  state.error = ''
  editing.value = true
}
function save() {
  run(async () => {
    const couple = await api(`couples/${state.couple.id}/`, { method: 'PATCH', body: form.value })
    state.couple.pet_name = couple.pet_name
    editing.value = false
    toast('Đã cập nhật bạn nhỏ! ♡')
  })
}
</script>

<template>
  <div class="page">
    <AppHeader title="Nhân vật của chúng ta">
      <button class="icon-button" aria-label="Đổi tên và loài thú cưng" @click="startEdit"><Pencil :size="20" /></button>
    </AppHeader>
    <div class="pet-stage">
      <span class="float-heart one">♡</span><span class="float-heart two">♡</span>
      <PetArt :stage="pet.stageIndex" :mood="bigMood" :aria-label="`${name}, giai đoạn ${stageLabel(pet.stageIndex, species)}`" role="img" />
    </div>
    <div class="pet-card">
      <button class="pet-name" @click="startEdit">{{ name }} <span class="heart">♡</span></button>
      <div v-if="moodFaces.length > 1" class="mood-picker" role="radiogroup" aria-label="Biểu cảm trên ảnh">
        <button type="button" role="radio" class="mood-auto" :aria-checked="!pickedMood" :class="{ chosen: !pickedMood }" :disabled="state.busy" @click="pickMood('')">Tự động</button>
        <button v-for="m in moodFaces" :key="m.face" type="button" role="radio" :aria-checked="pickedMood === m.face" :class="{ chosen: pickedMood === m.face }"
                :aria-label="m.label" :title="m.label" :disabled="state.busy" @click="pickMood(m.face)"><PetArt :mood="m.face" face /></button>
      </div>
      <p class="mood-chip"><PetArt :mood="pet.mood.face" face /> Tâm trạng: {{ pet.mood.text }}</p>
      <div class="pet-progress">
        <div class="progress-head"><strong>Giai đoạn: {{ stageLabel(pet.stageIndex, species) }}</strong><span class="chip soft">Cấp {{ pet.level }}</span></div>
        <div class="progress-track" role="progressbar" :aria-valuenow="pet.count" :aria-valuemax="pet.target" aria-label="Tiến trình phát triển">
          <span class="progress-fill" :style="{ width: Math.min(100, (pet.count / pet.target) * 100) + '%' }"></span>
          <PetArt mood="happy" face class="progress-pet" />
        </div>
        <p class="progress-text"><strong>{{ pet.count }} / {{ pet.target }} điểm</strong></p>
        <p class="muted center">{{ pet.next ? `Còn ${remaining} điểm để lên giai đoạn ${pet.next.label} nhé!` : `Còn ${remaining} điểm để lên cấp ${pet.level + 1} nhé!` }}</p>
        <p class="muted center pet-points-hint">Mỗi kỷ niệm +{{ MEMORY_POINTS }} điểm · mỗi câu đố được trả lời +{{ QUIZ_POINTS }} điểm</p>
      </div>
      <button class="btn primary block" @click="navigate('capture')">Lưu thêm kỷ niệm để nuôi {{ name }} lớn lên ♡</button>
      <button class="btn outline block" @click="navigate('quiz')">Chơi đố vui để thêm điểm cho {{ name }}</button>
    </div>
    <ol class="stage-row" aria-label="Các giai đoạn phát triển">
      <template v-for="(stage, i) in STAGES" :key="stage.label">
        <li :class="{ current: i === pet.stageIndex, reached: i <= pet.stageIndex }">
          <PetArt :stage="i" />
          <strong>{{ stageLabel(i, species) }}</strong><small>{{ stage.levels }}</small>
        </li>
        <ArrowRight v-if="i < STAGES.length - 1" :size="16" class="stage-arrow" aria-hidden="true" />
      </template>
    </ol>

    <BottomSheet v-if="editing" title="Bạn nhỏ của chúng ta ♡" @close="editing = false">
      <form class="stack" @submit.prevent="save">
        <label class="field">Tên bạn nhỏ<input v-model="form.pet_name" required maxlength="50" placeholder="Bờm" /></label>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Lưu</button>
      </form>
    </BottomSheet>
  </div>
</template>
