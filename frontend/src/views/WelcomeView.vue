<script setup>
import { ref } from 'vue'
import { ArrowRight, ChevronLeft } from 'lucide-vue-next'
import { api } from '@/api.js'
import { art } from '@/characters.js'
import GoogleButton from '@/components/GoogleButton.vue'
import JarArt from '@/components/JarArt.vue'
import { state, run, signIn } from '@/store.js'

const slides = [
  { title: 'Lưu giữ những điều ngọt ngào', text: 'Cùng nhau tạo nên một góc nhỏ để lưu kỷ niệm, vun đắp tình yêu và trân trọng những khoảnh khắc.', image: 'couple' },
  { title: 'Lưu giữ kỷ niệm vào những hũ yêu thương', text: 'Mỗi chuyến đi, mỗi buổi hẹn là một chiếc hũ nhỏ trong Tủ Thương của hai bạn.', jars: true },
  { title: 'Nuôi thú cưng chung của hai chúng ta', text: 'Mỗi kỷ niệm mới giúp bạn nhỏ lớn lên từng ngày.', image: 'male-3' },
]
const slide = ref(0)
const step = ref('intro') // intro | register | login
const form = ref({})

function open(next) { step.value = next; form.value = {}; state.error = '' }
function submit() {
  run(async () => {
    const data = await api(`auth/${step.value}/`, { method: 'POST', body: form.value })
    if (step.value === 'register') state.onboarding = 'profile'
    await signIn(data.token)
  })
}
function googleSignIn(credential) {
  run(async () => {
    const data = await api('auth/google/', { method: 'POST', body: { credential } })
    if (data.created) state.onboarding = 'profile'
    await signIn(data.token)
  })
}
</script>

<template>
  <section v-if="step === 'intro'" class="screen welcome">
    <div class="brand-lockup">
      <img :src="art['logo-jar']" alt="" class="brand-jar" />
      <h1 class="wordmark">Love Cabinet<br />Tủ Thương <span class="heart">♡</span></h1>
      <p>Góc nhỏ lưu giữ những điều ngọt ngào của hai chúng ta.</p>
    </div>
    <div class="slide" @click="slide = (slide + 1) % slides.length">
      <div class="slide-art">
        <div v-if="slides[slide].jars" class="mini-shelf"><JarArt color="#F6C9C4" :emojis="['❤️', '🍰', '☕', '🎂']" /><JarArt color="#BFD7EA" :emojis="['⛰️', '🌲', '📷']" /></div>
        <img v-else :src="art[slides[slide].image]" alt="" />
      </div>
      <h2>{{ slides[slide].title }} <span class="heart">♡</span></h2>
      <p>{{ slides[slide].text }}</p>
    </div>
    <div class="dots" role="tablist" aria-label="Giới thiệu">
      <button v-for="(s, i) in slides" :key="i" role="tab" :aria-selected="slide === i" :aria-label="`Trang ${i + 1}`" :class="{ active: slide === i }" @click="slide = i"></button>
    </div>
    <div class="welcome-actions">
      <button class="btn primary block" @click="open('register')">Bắt đầu <ArrowRight :size="18" /></button>
      <button class="link-button" @click="open('login')">Đã có tài khoản? <strong>Đăng nhập</strong></button>
      <GoogleButton @credential="googleSignIn" />
      <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
    </div>
  </section>

  <section v-else class="screen form-screen">
    <button class="icon-button back-corner" aria-label="Quay lại" @click="open('intro')"><ChevronLeft :size="24" /></button>
    <template v-if="step === 'register'">
      <h1 class="screen-title">Tạo hồ sơ<br />của bạn <span class="heart">♡</span></h1>
      <p class="screen-lead">Để kết nối, hãy cho mình biết một chút về bạn nhé!</p>
      <div class="profile-art"><img :src="art['female-happy']" alt="" /></div>
    </template>
    <template v-else>
      <h1 class="screen-title">Chào mừng<br />trở lại <span class="heart">♡</span></h1>
      <p class="screen-lead">Tủ Thương của hai bạn vẫn đang chờ đấy.</p>
      <div class="profile-art"><img :src="art['couple']" alt="" class="wide" /></div>
    </template>
    <form class="stack" @submit.prevent="submit">
      <label v-if="step === 'register'" class="field"><span class="label-text">Tên hiển thị <span class="required">*</span></span><input v-model="form.display_name" required maxlength="100" placeholder="Bạn tên là gì?" /></label>
      <label class="field">Tên đăng nhập<input v-model="form.username" required maxlength="150" autocomplete="username" /></label>
      <label class="field">Mật khẩu<input v-model="form.password" type="password" required :minlength="step === 'register' ? 8 : 1" :autocomplete="step === 'register' ? 'new-password' : 'current-password'" /></label>
      <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
      <button class="btn primary block" :disabled="state.busy">{{ state.busy ? 'Đang xử lý…' : step === 'register' ? 'Tiếp tục' : 'Vào Tủ Thương' }}</button>
      <button type="button" class="link-button" @click="open(step === 'register' ? 'login' : 'register')">{{ step === 'register' ? 'Đã có tài khoản? Đăng nhập' : 'Chưa có tài khoản? Tạo hồ sơ' }}</button>
    </form>
    <GoogleButton @credential="googleSignIn" />
  </section>
</template>
