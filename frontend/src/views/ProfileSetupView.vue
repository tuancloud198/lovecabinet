<script setup>
import { ref } from 'vue'
import { api } from '@/api.js'
import { state, run } from '@/store.js'

const form = ref({ gender: state.me.gender || '', birth_date: state.me.birth_date || '', bio: state.me.bio || '' })
function save() {
  run(async () => {
    state.me = await api('users/me/', { method: 'PATCH', body: { ...form.value, birth_date: form.value.birth_date || null } })
    state.onboarding = ''
  })
}
</script>

<template>
  <section class="screen form-screen">
    <h1 class="screen-title">Hoàn thiện hồ sơ</h1>
    <ol class="steps" aria-label="Tiến trình">
      <li class="done"></li><li class="done"></li><li class="current"></li><li></li><li></li>
    </ol>
    <form class="stack" @submit.prevent="save">
      <fieldset class="field">
        <legend>Giới tính</legend>
        <div class="segmented">
          <button type="button" :class="{ active: form.gender === 'Nam' }" @click="form.gender = 'Nam'">Nam ♂</button>
          <button type="button" :class="{ active: form.gender === 'Nữ' }" @click="form.gender = 'Nữ'">Nữ ♀</button>
        </div>
      </fieldset>
      <label class="field">Ngày sinh<input v-model="form.birth_date" type="date" /></label>
      <label class="field"><span class="label-text">Giới thiệu <span class="muted">(tùy chọn)</span></span>
        <textarea v-model="form.bio" maxlength="120" rows="3" placeholder="Thích du lịch, đi cafe, yêu ký ức dâng những khoảnh khắc nhỏ…"></textarea>
        <span class="counter">{{ form.bio.length }}/120</span>
      </label>
      <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
      <button class="btn primary block" :disabled="state.busy">Tiếp tục</button>
      <button type="button" class="link-button" @click="state.onboarding = ''">Để sau</button>
    </form>
  </section>
</template>
