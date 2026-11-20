<script setup>
import { ref, onMounted } from 'vue'
import { LogOut, Pencil } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate } from '@/format.js'
import { state, partner, run, signOut, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import UserTag from '@/components/UserTag.vue'
import { THEMES, theme, applyTheme } from '@/theme.js'

// Release check: both versions are the image tags, so after a deploy you can see it went live.
const frontendVersion = import.meta.env.VITE_APP_VERSION || 'dev'
const backendVersion = ref('…')
onMounted(() => api('auth/config/').then(data => { backendVersion.value = data.version || 'dev' }).catch(() => { backendVersion.value = '?' }))
const editing = ref(false)
const form = ref({})
function startEdit() {
  const { display_name, gender, birth_date, bio } = state.me
  form.value = { display_name, gender, birth_date: birth_date || '', bio }
  state.error = ''
  editing.value = true
}
function save() {
  run(async () => {
    state.me = await api('users/me/', { method: 'PATCH', body: { ...form.value, birth_date: form.value.birth_date || null } })
    const member = state.couple.members.find(m => m.id === state.me.id)
    if (member) Object.assign(member, state.me)
    editing.value = false
    toast('Đã lưu hồ sơ!')
  })
}
</script>

<template>
  <div class="page">
    <AppHeader title="Hồ sơ">
      <button class="icon-button" aria-label="Chỉnh sửa hồ sơ" @click="startEdit"><Pencil :size="20" /></button>
    </AppHeader>
    <section class="profile-card card">
      <CharacterAvatar :user="state.me" mood="happy" :size="112" />
      <h2>{{ state.me.display_name }}</h2>
      <p class="muted">@{{ state.me.username }}</p>
      <UserTag :tag="state.me.tag" class="big-tag" />
      <div class="chips">
        <span v-if="state.me.gender" class="chip soft">{{ state.me.gender === 'Nam' ? 'Nam ♂' : state.me.gender === 'Nữ' ? 'Nữ ♀' : state.me.gender }}</span>
        <span v-if="state.me.birth_date" class="chip soft">🎂 {{ displayDate(state.me.birth_date) }}</span>
      </div>
      <p class="bio">{{ state.me.bio || 'Chưa có lời giới thiệu.' }}</p>
    </section>
    <section v-if="partner" class="card partner-card">
      <h3>Đã kết nối với <span class="heart">♡</span></h3>
      <div class="partner-row">
        <CharacterAvatar :user="partner" mood="happy" :size="56" />
        <div><strong>{{ partner.display_name }}</strong><small class="muted">{{ partner.tag }}</small></div>
      </div>
      <div class="stats">
        <div><strong>{{ state.memories.length }}</strong><small>kỷ niệm</small></div>
        <div><strong>{{ state.jars.length }}</strong><small>hũ</small></div>
        <div><strong>{{ state.events.length }}</strong><small>sự kiện</small></div>
      </div>
    </section>
    <section class="card theme-card">
      <h3>Giao diện theo mùa</h3>
      <div class="theme-grid" role="radiogroup" aria-label="Giao diện">
        <button v-for="t in THEMES" :key="t.key" type="button" role="radio" :aria-checked="theme === t.key" :class="{ chosen: theme === t.key }" @click="applyTheme(t.key)">
          <span class="theme-dot" :style="{ background: t.color }">{{ t.icon }}</span>{{ t.label }}
        </button>
      </div>
    </section>
    <button class="btn outline block" :disabled="state.busy" @click="signOut"><LogOut :size="18" /> Đăng xuất</button>
    <p class="app-version">Phiên bản giao diện {{ frontendVersion }} · máy chủ {{ backendVersion }}</p>

    <BottomSheet v-if="editing" title="Hồ sơ của bạn ♡" @close="editing = false">
      <form class="stack" @submit.prevent="save">
        <label class="field">Tên hiển thị<input v-model="form.display_name" required maxlength="100" /></label>
        <fieldset class="field"><legend>Giới tính</legend>
          <div class="segmented">
            <button type="button" :class="{ active: form.gender === 'Nam' }" @click="form.gender = 'Nam'">Nam ♂</button>
            <button type="button" :class="{ active: form.gender === 'Nữ' }" @click="form.gender = 'Nữ'">Nữ ♀</button>
          </div>
        </fieldset>
        <label class="field">Ngày sinh<input v-model="form.birth_date" type="date" /></label>
        <label class="field">Giới thiệu<textarea v-model="form.bio" maxlength="120" rows="3"></textarea><span class="counter">{{ form.bio.length }}/120</span></label>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Lưu</button>
      </form>
    </BottomSheet>
  </div>
</template>
