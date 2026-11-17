<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ArrowRight, Check, ChevronLeft, ChevronRight, Hourglass, Keyboard } from 'lucide-vue-next'
import { api } from '@/api.js'
import { art } from '@/characters.js'
import { state, run, load, refreshPairing, signOut } from '@/store.js'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import UserTag from '@/components/UserTag.vue'

const entering = ref(false)
const code = ref('')
const chars = computed(() => code.value.split(''))
const received = computed(() => state.invites.received[0])
const sent = computed(() => state.invites.sent[0])

function normalize(event) {
  code.value = event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)
  event.target.value = code.value
}
function invite() {
  run(async () => {
    await api('couple-invitations/', { method: 'POST', body: { tag: '#' + code.value } })
    code.value = ''
    entering.value = false
    await load()
  })
}
function respond(action) {
  run(async () => {
    await api(`couple-invitations/${received.value.id}/${action}/`, { method: 'POST' })
    await load()
    if (state.couple) state.justPaired = true
  })
}

// While waiting (our invite pending, or for someone to invite us), check every few
// seconds — one lightweight request, and only while the tab is visible and the user
// isn't in the middle of typing a code or answering an invitation.
const POLL_MS = 5000
let timer
async function poll() {
  if (document.hidden || state.busy || state.justPaired || entering.value || received.value) return
  try {
    await refreshPairing()
    if (state.couple) state.justPaired = true
  } catch { /* keep polling */ }
}
function onVisibility() { if (!document.hidden) poll() }
onMounted(() => {
  timer = setInterval(poll, POLL_MS)
  document.addEventListener('visibilitychange', onVisibility)
})
onBeforeUnmount(() => {
  clearInterval(timer)
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <!-- 10. Đã ghép đôi thành công -->
  <section v-if="state.justPaired" class="screen center-screen">
    <img :src="art.couple" alt="" class="hero-art" />
    <h1 class="screen-title">Đã ghép đôi thành công!</h1>
    <p class="screen-lead">Giờ đây, hai bạn đã có Tủ Thương chung để lưu giữ những kỷ niệm thật đẹp cùng nhau!</p>
    <button class="btn primary block" @click="state.justPaired = false">Vào Tủ Thương <ArrowRight :size="18" /></button>
  </section>

  <!-- 9. Lời mời ghép đôi -->
  <section v-else-if="received" class="screen center-screen">
    <h1 class="screen-title">Lời mời ghép đôi <span class="heart">♡</span></h1>
    <span class="success-badge"><Check :size="34" stroke-width="3" /></span>
    <CharacterAvatar :user="received.sender" mood="happy" :size="88" />
    <p class="invite-from"><strong>{{ received.sender.display_name }}</strong> <span class="muted">{{ received.sender.tag }}</span><br />muốn kết nối với bạn trên Love Cabinet.</p>
    <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
    <button class="btn primary block" :disabled="state.busy" @click="respond('accept')">Đồng ý ghép đôi</button>
    <button class="btn outline block" :disabled="state.busy" @click="respond('decline')">Từ chối</button>
  </section>

  <!-- 7. Nhập mã ghép đôi -->
  <section v-else-if="entering" class="screen form-screen">
    <button class="icon-button back-corner" aria-label="Quay lại" @click="entering = false; state.error = ''"><ChevronLeft :size="24" /></button>
    <h1 class="screen-title">Nhập mã ghép đôi</h1>
    <p class="screen-lead">Hãy nhập mã 8 ký tự mà người ấy đã gửi cho bạn.</p>
    <form class="stack" @submit.prevent="invite">
      <label class="code-boxes">
        <span class="visually-hidden">Mã của người ấy</span>
        <input :value="code" inputmode="text" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="9" @input="normalize" />
        <span class="hash">#</span>
        <span v-for="i in 8" :key="i" class="box" :class="{ filled: chars[i - 1], current: i - 1 === chars.length }">{{ chars[i - 1] }}</span>
      </label>
      <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
      <button class="btn primary block" :disabled="state.busy || code.length !== 8">Kết nối ngay</button>
      <p class="hint">Bạn chưa có mã? Mã của bạn là <UserTag :tag="state.me.tag" /></p>
    </form>
  </section>

  <!-- 8. Đang chờ xác nhận -->
  <section v-else-if="sent" class="screen center-screen">
    <h1 class="screen-title">Đang chờ xác nhận…</h1>
    <p class="screen-lead">Đã gửi lời mời ghép đôi đến <strong>{{ sent.recipient.display_name }}</strong>, hãy chờ họ xác nhận nhé!</p>
    <div class="waiting-row">
      <CharacterAvatar :user="state.me" :size="72" />
      <span class="waiting-dots">• • <span class="hourglass"><Hourglass :size="18" /></span> • •</span>
      <CharacterAvatar :user="sent.recipient" :size="72" />
    </div>
    <img :src="art.couple" alt="" class="hero-art" />
    <button class="btn outline block" :disabled="state.busy" @click="run(load)">Kiểm tra lại</button>
  </section>

  <!-- 6. Chọn cách ghép đôi -->
  <section v-else class="screen center-screen">
    <h1 class="screen-title">Ghép đôi<br />với người ấy <span class="heart">♡</span></h1>
    <p class="screen-lead">Kết nối để cùng nhau tạo nên Tủ Thương của hai đứa.</p>
    <img :src="art.couple" alt="" class="hero-art" />
    <div class="card my-code">
      <span class="muted">Mã của bạn · gửi cho người ấy</span>
      <UserTag :tag="state.me.tag" class="big-tag" />
    </div>
    <button class="list-row card" @click="entering = true; state.error = ''">
      <span class="row-icon"><Keyboard :size="20" /></span><span class="row-text">Nhập mã ghép đôi</span><ChevronRight :size="20" />
    </button>
    <button class="link-button" @click="signOut">Đăng xuất</button>
  </section>
</template>
