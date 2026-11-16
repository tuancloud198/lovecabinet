<script setup>
import { ref, computed } from 'vue'
import { ArrowRight, Pencil } from 'lucide-vue-next'
import { api } from '@/api.js'
import { petStatus, PET_SPECIES, STAGES, stageLabel } from '@/characters.js'
import { state, navigate, run, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import PetArt from '@/components/PetArt.vue'

const pet = computed(() => petStatus(state.memories))
const species = computed(() => state.couple.pet_type || 'dog')
const name = computed(() => state.couple.pet_name)
const remaining = computed(() => pet.value.target - pet.value.count)

const editing = ref(false)
const form = ref({})
function startEdit() {
  form.value = { pet_name: name.value, pet_type: species.value }
  state.error = ''
  editing.value = true
}
function save() {
  run(async () => {
    const couple = await api(`couples/${state.couple.id}/`, { method: 'PATCH', body: form.value })
    Object.assign(state.couple, { pet_name: couple.pet_name, pet_type: couple.pet_type })
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
      <PetArt :species="species" :stage="pet.stageIndex" :mood="pet.mood.face" :aria-label="`${name}, giai đoạn ${stageLabel(species, pet.stageIndex)}`" role="img" />
    </div>
    <div class="pet-card">
      <button class="pet-name" @click="startEdit">{{ name }} <span class="heart">♡</span></button>
      <p class="mood-chip"><PetArt :species="species" :mood="pet.mood.face" face /> Tâm trạng: {{ pet.mood.text }}</p>
      <div class="pet-progress">
        <div class="progress-head"><strong>Giai đoạn: {{ stageLabel(species, pet.stageIndex) }}</strong><span class="chip soft">Cấp {{ pet.level }}</span></div>
        <div class="progress-track" role="progressbar" :aria-valuenow="pet.count" :aria-valuemax="pet.target" aria-label="Tiến trình phát triển">
          <span class="progress-fill" :style="{ width: Math.min(100, (pet.count / pet.target) * 100) + '%' }"></span>
          <PetArt :species="species" mood="happy" face class="progress-pet" />
        </div>
        <p class="progress-text"><strong>{{ pet.count }} / {{ pet.target }}</strong></p>
        <p class="muted center">{{ pet.next ? `Còn ${remaining} kỷ niệm để lên giai đoạn ${pet.next.label} nhé!` : `Còn ${remaining} kỷ niệm để lên cấp ${pet.level + 1} nhé!` }}</p>
      </div>
      <button class="btn primary block" @click="navigate('capture')">Lưu thêm kỷ niệm để nuôi {{ name }} lớn lên ♡</button>
    </div>
    <ol class="stage-row" aria-label="Các giai đoạn phát triển">
      <template v-for="(stage, i) in STAGES" :key="stage.label">
        <li :class="{ current: i === pet.stageIndex, reached: i <= pet.stageIndex }">
          <PetArt :species="species" :stage="i" />
          <strong>{{ stageLabel(species, i) }}</strong><small>{{ stage.levels }}</small>
        </li>
        <ArrowRight v-if="i < STAGES.length - 1" :size="16" class="stage-arrow" aria-hidden="true" />
      </template>
    </ol>

    <BottomSheet v-if="editing" title="Bạn nhỏ của chúng ta ♡" @close="editing = false">
      <form class="stack" @submit.prevent="save">
        <label class="field">Tên bạn nhỏ<input v-model="form.pet_name" required maxlength="50" placeholder="Bờm" /></label>
        <fieldset class="field">
          <legend>Chọn loài</legend>
          <div class="species-grid" role="radiogroup">
            <button v-for="s in PET_SPECIES" :key="s.key" type="button" role="radio" :aria-checked="form.pet_type === s.key" :class="{ chosen: form.pet_type === s.key }" @click="form.pet_type = s.key">
              <PetArt :species="s.key" mood="happy" /><span>{{ s.label }}</span>
            </button>
          </div>
        </fieldset>
        <p class="muted species-note">Đổi loài không làm mất tiến trình — bạn nhỏ vẫn giữ cấp độ hiện tại.</p>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Lưu</button>
      </form>
    </BottomSheet>
  </div>
</template>
