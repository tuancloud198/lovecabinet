<script setup>
import { ref, computed, onMounted } from 'vue'
import { Heart, Archive, CalendarDays, Camera, UserRound, LogOut, Plus, ArrowLeft, X, Dog, Settings, MessageCircle } from 'lucide-vue-next'
import PrivatePhoto from './PrivatePhoto.vue'
const token = ref(sessionStorage.getItem('token') || '')
const me = ref(null), couple = ref(null), cabinets = ref([]), jars = ref([]), memories = ref([]), events = ref([])
const tab = ref('cabinet'), selected = ref(null), detail = ref(null), modal = ref(''), error = ref(''), busy = ref(false), register = ref(false), code = ref(''), invitation = ref(''), search = ref(''), year = ref(new Date().getFullYear())
const form = ref({}), files = ref([]), comment = ref('')
const today = () => new Date().toLocaleDateString('en-CA')
const visibleJars = computed(() => jars.value.filter(j => cabinets.value.some(c => c.id === j.cabinet && c.year === Number(year.value)) && j.name.toLowerCase().includes(search.value.toLowerCase())))
const jarMemories = computed(() => memories.value.filter(m => m.jar === selected.value?.id))
const years = computed(() => [...new Set([new Date().getFullYear(), ...cabinets.value.map(c => c.year)])].sort().reverse())
const upcoming = computed(() => [...events.value].filter(e => e.date >= today()).sort((a,b) => a.date.localeCompare(b.date)))
const emojis = ['❤️','😍','🎂','🌷','☕','✨','🎁','✈️','🌲','📷','🌙','🎮']
const exp = computed(() => memories.value.length % 10 * 10)
async function api(path, options = {}) {
  const isForm = options.body instanceof FormData
  const response = await fetch(`/api/${path}`, { ...options, headers: { ...(isForm ? {} : { 'Content-Type': 'application/json' }), ...(token.value ? { Authorization: `Token ${token.value}` } : {}), ...options.headers }, body: options.body ? (isForm ? options.body : JSON.stringify(options.body)) : undefined })
  if (response.status === 204) return null
  const data = await response.json()
  if (!response.ok) {
    if (response.status === 401) { token.value = ''; sessionStorage.removeItem('token') }
    throw new Error(typeof data === 'string' ? data : Object.entries(data).map(([k,v]) => `${k === 'detail' ? '' : k + ': '}${Array.isArray(v) ? v.join(' ') : v}`).join(' '))
  }
  return data
}
async function run(fn) { if (busy.value) return; busy.value = true; error.value = ''; try { await fn() } catch (e) { error.value = e.message } finally { busy.value = false } }
async function load() {
  me.value = await api('users/me/')
  const couples = await api('couples/')
  couple.value = couples[0] || null
  if (couple.value) [cabinets.value, jars.value, memories.value, events.value] = await Promise.all(['cabinets/','jars/','memories/','events/'].map(p => api(p)))
}
function auth() { run(async () => { const data = await api(`auth/${register.value ? 'register' : 'login'}/`, { method: 'POST', body: form.value }); token.value = data.token; sessionStorage.setItem('token', data.token); form.value = {}; await load() }) }
function open(type) { error.value = ''; files.value = []; form.value = type === 'memory' ? { jar: selected.value?.id || jars.value[0]?.id, date: today(), emoji: '❤️', story: '' } : type === 'event' ? { date: today(), emoji: '🎂' } : type === 'profile' ? { ...me.value } : { emoji: '❤️', color: '#FBE5DD' }; modal.value = type }
function save() { run(async () => {
  if (modal.value === 'profile') { await api('users/me/', { method: 'PATCH', body: form.value }) }
  else if (modal.value === 'jar') {
    let cabinet = cabinets.value.find(c => c.year === Number(year.value))
    if (!cabinet) cabinet = await api('cabinets/', { method: 'POST', body: { name: 'Tủ thương', year: Number(year.value) } })
    await api('jars/', { method: 'POST', body: { ...form.value, cabinet: cabinet.id } })
  } else if (modal.value === 'memory') {
    let memory = form.value.id ? form.value : await api('memories/', { method: 'POST', body: form.value })
    form.value = { ...form.value, id: memory.id }
    while (files.value.length) {
      const body = new FormData(); body.append('memory', memory.id); body.append('file', files.value[0]); await api('photos/', { method: 'POST', body }); files.value.shift()
    }
  } else await api('events/', { method: 'POST', body: form.value })
  modal.value = ''; await load()
}) }
async function refreshDetail() { await load(); detail.value = memories.value.find(m => m.id === detail.value?.id) || null }
function react() { run(async () => { await api(`memories/${detail.value.id}/react/`, { method: 'POST' }); await refreshDetail() }) }
function addComment() { run(async () => { await api(`memories/${detail.value.id}/comment/`, { method: 'POST', body: { text: comment.value } }); comment.value = ''; await refreshDetail() }) }
function remove(type, id) { if (window.confirm('Bạn có chắc muốn xóa?')) run(async () => { await api(`${type}/${id}/`, { method: 'DELETE' }); detail.value = null; if (type === 'jars') selected.value = null; await load() }) }
function logout() { run(async () => { await api('auth/logout/', { method: 'POST' }); sessionStorage.removeItem('token'); token.value = ''; me.value = null; couple.value = null; selected.value = null; detail.value = null; form.value = {}; memories.value = []; jars.value = [] }) }
onMounted(() => { if (token.value) run(load) })
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <a class="brand" href="/">♡ <span>Tủ Thương<small>LOVE CABINET</small></span></a>
      <p class="sidebar-note">Một góc nhỏ,<br>thật nhiều yêu thương.</p>
      <nav v-if="me && couple">
        <button v-for="item in [['cabinet','Tủ thương',Archive],['calendar','Lịch của chúng ta',CalendarDays],['pet','Bạn nhỏ',Dog],['profile','Hồ sơ',UserRound]]" :class="{ active: tab === item[0] }" @click="tab = item[0]; selected = null; detail = null"><component :is="item[2]" :size="20"/>{{ item[1] }}</button>
      </nav>
      <div class="sidebar-bottom"><span>Gói ghém từng khoảnh khắc ♡</span><button v-if="me" @click="logout" aria-label="Đăng xuất"><LogOut :size="18"/> Đăng xuất</button></div>
    </aside>
    <main>
      <div v-if="error" class="alert" role="alert">{{ error }}<button @click="error = ''" aria-label="Đóng lỗi"><X :size="16"/></button></div>
      <div v-if="busy" class="loading" role="status">Đang xử lý…</div>
      <section v-if="!token" class="welcome">
        <div class="eyebrow">NƠI YÊU THƯƠNG ĐƯỢC CẤT GIỮ</div><div class="welcome-art">🐶 ♡ 🐶</div>
        <h1>Lưu giữ những<br><em>điều ngọt ngào.</em></h1><p>Cùng nhau tạo nên một góc nhỏ để lưu kỷ niệm,<br>và trân trọng những khoảnh khắc của hai chúng ta.</p>
        <form class="auth-card" @submit.prevent="auth">
          <h2>{{ register ? 'Bắt đầu câu chuyện của bạn' : 'Chào mừng trở lại ♡' }}</h2>
          <label v-if="register">Tên hiển thị<input v-model="form.display_name" required maxlength="100" placeholder="Bạn tên là gì?"></label>
          <label>Tên đăng nhập<input v-model="form.username" required autocomplete="username" maxlength="150"></label>
          <label>Mật khẩu<input v-model="form.password" required type="password" :autocomplete="register ? 'new-password' : 'current-password'" :minlength="register ? 8 : 1"></label>
          <button class="primary" :disabled="busy">{{ register ? 'Tạo tài khoản →' : 'Vào Tủ thương →' }}</button>
          <button type="button" class="text-button" @click="register = !register; form = {}; error = ''">{{ register ? 'Đã có tài khoản? Đăng nhập' : 'Chưa có tài khoản? Bắt đầu' }}</button>
        </form>
      </section>
      <section v-else-if="me && !couple" class="welcome pairing">
        <span class="eyebrow">MỘT CÂU CHUYỆN DÀNH CHO HAI NGƯỜI</span><div class="welcome-art">🐶 ♡ 🐶</div><h1>Ghép đôi<br><em>với người ấy.</em></h1><p>Xin chào {{ me.display_name }}! Mời một người cùng bạn<br>lấp đầy chiếc tủ bằng những điều đáng nhớ.</p>
        <div class="auth-card"><h2>Gửi một lời mời ♡</h2><button class="primary" :disabled="busy" @click="run(async () => { invitation = (await api('couple-invitations/', { method: 'POST' })).code })">Tạo mã ghép đôi</button><div v-if="invitation" class="invite-code">{{ invitation }}<small>Gửi mã này cho người ấy · Có hiệu lực 48 giờ</small></div><hr><form @submit.prevent="run(async () => { await api('couple-invitations/accept/', { method: 'POST', body: { code } }); await load() })"><label>Đã nhận được mã?<input v-model="code" required maxlength="10" placeholder="Nhập mã từ người ấy"></label><button class="secondary" :disabled="busy">Đồng ý ghép đôi ♡</button></form><button class="text-button" @click="run(load)">Tôi đã gửi mã · Kiểm tra kết nối</button></div>
      </section>
      <template v-else-if="couple">
        <header class="topbar"><span>GÓC NHỎ CỦA HAI CHÚNG TA</span><button class="avatar" @click="tab = 'profile'">{{ me.display_name?.charAt(0) }}<Heart :size="14"/></button></header>
        <template v-if="tab === 'cabinet'">
          <template v-if="!selected">
            <div class="page-heading"><div><span class="eyebrow">MỖI KỶ NIỆM, MỘT CHÚT YÊU THƯƠNG</span><h1>Tủ thương của chúng ta <span class="heart">♡</span></h1><p>Cất giữ những điều bình dị, để ngày nào cũng đáng nhớ.</p></div><button class="primary" @click="open('jar')"><Plus :size="18"/> Thêm hũ mới</button></div>
            <section class="together-banner"><div><span class="badge">{{ couple.members.map(m => m.display_name).join(' & ') }}</span><h2>Hai người. Một chiếc tủ.<br>Vô vàn điều dễ thương.</h2><p>Hôm nay, mình lưu lại điều gì nhỉ?</p><button class="secondary" :disabled="!jars.length" @click="open('memory')"><Camera :size="18"/> Lưu kỷ niệm</button></div><div class="banner-art" aria-hidden="true"><span>♡</span><div>🐶 🐶</div><small>cùng nhau, từng chút một.</small></div></section>
            <div class="collection-toolbar"><h2>Những hũ yêu thương <small>{{ visibleJars.length }} hũ</small></h2><div><input v-model="search" aria-label="Tìm hũ" placeholder="Tìm một chiếc hũ…"><select v-model="year" aria-label="Năm"><option v-for="y in years">{{ y }}</option></select></div></div>
            <div v-if="!visibleJars.length" class="empty"><Archive :size="42"/><h2>{{ search ? 'Chưa tìm thấy chiếc hũ này' : 'Chiếc tủ đang chờ câu chuyện đầu tiên' }}</h2><p>Tạo một hũ nhỏ cho chuyến đi, ngày đặc biệt hay những buổi cà phê.</p><button class="primary" @click="open('jar')">+ Tạo hũ yêu thương</button></div>
            <div class="jar-grid"><button v-for="jar in visibleJars" class="jar-card" @click="selected = jar"><div class="jar-scene" :style="{ '--jar-color': jar.color }"><div class="jar-lid"></div><div class="glass-jar"><span class="ribbon">🎀</span><div class="jar-emojis"><span v-for="emoji in [jar.emoji, ...memories.filter(m => m.jar === jar.id).slice(0,5).map(m => m.emoji)]">{{ emoji }}</span></div></div><span class="sparkle">✦</span></div><h3>{{ jar.name }}</h3><p>{{ memories.filter(m => m.jar === jar.id).length }} kỷ niệm <span>↗</span></p></button><button class="new-jar" @click="open('jar')"><span>+</span><h3>Một hũ mới</h3><p>Cho những điều sắp tới ♡</p></button></div>
            <div class="footer-note">♡ &nbsp; Những điều nhỏ bé làm nên câu chuyện lớn của chúng ta.</div>
          </template>
          <template v-else>
            <button class="back" @click="selected = null"><ArrowLeft :size="18"/> Về tủ thương</button><div class="page-heading"><div><span class="eyebrow">CHIẾC HŨ CỦA NHỮNG KHOẢNH KHẮC</span><h1>{{ selected.emoji }} {{ selected.name }}</h1><p>{{ jarMemories.length }} kỷ niệm được cất giữ bằng yêu thương.</p></div><button class="primary" @click="open('memory')"><Plus :size="18"/> Lưu kỷ niệm</button></div>
            <div v-if="!jarMemories.length" class="empty"><Camera :size="42"/><h2>Chưa có kỷ niệm nào</h2><p>Thêm một bức ảnh và kể câu chuyện đầu tiên của hai bạn.</p></div>
            <div class="memory-grid"><button v-for="m in jarMemories" class="memory-card" @click="detail = m"><PrivatePhoto v-if="m.photos[0]" :url="m.photos[0].url"/><div v-else class="memory-cover">{{ m.emoji }}</div><div><small>{{ m.date }}</small><h3>{{ m.emoji }} {{ m.title }}</h3><p>{{ m.story }}</p><span>♡ {{ m.likes }} &nbsp; · &nbsp; {{ m.comments.length }} bình luận</span></div></button></div><button class="text-button danger" @click="remove('jars', selected.id)">Xóa hũ và các kỷ niệm trong hũ</button>
          </template>
        </template>
        <template v-if="tab === 'calendar'"><div class="page-heading"><div><span class="eyebrow">NHỮNG NGÀY MÌNH MONG CHỜ</span><h1>Lịch của chúng ta ♡</h1><p>Một lời nhắc cho những ngày thật đặc biệt.</p></div><button class="primary" @click="open('event')"><Plus :size="18"/> Thêm sự kiện</button></div><div class="panel"><h2>Sự kiện sắp tới</h2><p v-if="!upcoming.length">Chưa có sự kiện sắp tới. Lên lịch một buổi hẹn nhé!</p><div v-for="e in upcoming" class="event-row"><span class="event-icon">{{ e.emoji }}</span><div><h3>{{ e.title }}</h3><p>{{ e.date }}</p></div><button class="icon-button" @click="remove('events', e.id)" aria-label="Xóa sự kiện"><X :size="18"/></button></div></div><div class="panel"><h2>Dòng thời gian kỷ niệm</h2><button v-for="m in [...memories].sort((a,b) => b.date.localeCompare(a.date))" class="timeline-row" @click="detail = m"><span>{{ m.date }}</span><strong>{{ m.emoji }} {{ m.title }}</strong></button><p v-if="!memories.length">Những kỷ niệm mới sẽ xuất hiện tại đây.</p></div></template>
        <template v-if="tab === 'pet'"><div class="page-heading"><div><span class="eyebrow">LỚN LÊN CÙNG NHỮNG KỶ NIỆM</span><h1>Bạn nhỏ của chúng ta ♡</h1></div></div><div class="pet-panel panel"><div class="pet-art">🐶</div><h2>{{ couple.pet_name }} ♡</h2><span class="badge">Cấp {{ Math.floor(memories.length / 10) + 1 }} · {{ memories.length < 10 ? 'Cún con' : memories.length < 30 ? 'Lớn dần' : 'Trưởng thành' }}</span><p>Mỗi kỷ niệm là một chút yêu thương giúp Bờm lớn lên.</p><progress :value="exp" max="100"></progress><p>{{ exp }} / 100 EXP · Còn {{ 10 - memories.length % 10 }} kỷ niệm để lên cấp</p><button class="primary" :disabled="!jars.length" @click="open('memory')">Lưu thêm kỷ niệm ♡</button></div></template>
        <template v-if="tab === 'profile'"><div class="page-heading"><div><span class="eyebrow">MỘT CHÚT VỀ BẠN</span><h1>Hồ sơ của bạn</h1></div><button class="secondary" @click="open('profile')"><Settings :size="18"/> Chỉnh sửa</button></div><div class="panel profile"><div class="large-avatar">{{ me.display_name?.charAt(0) }}</div><h2>{{ me.display_name }}</h2><p>@{{ me.username }}</p><p>{{ me.bio || 'Chưa có lời giới thiệu.' }}</p><p v-if="me.birth_date">Ngày sinh: {{ me.birth_date }}</p><hr><h3>Đã kết nối với ♡</h3><p>{{ couple.members.filter(m => m.id !== me.id).map(m => m.display_name).join(', ') }}</p><button class="text-button" @click="logout">Đăng xuất</button></div></template>
      </template>
      <nav v-if="couple" class="mobile-nav"><button v-for="item in [['calendar','Lịch',CalendarDays],['cabinet','Tủ',Archive],['pet','Bạn nhỏ',Dog],['profile','Hồ sơ',UserRound]]" :class="{active: tab === item[0]}" @click="tab = item[0]; selected = null"><component :is="item[2]" :size="22"/>{{ item[1] }}</button></nav>
    </main>
    <div v-if="modal" class="modal-backdrop" @click.self="!busy && (modal = '')"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><button class="close icon-button" @click="modal = ''" :disabled="busy" aria-label="Đóng"><X/></button><span class="eyebrow">THÊM MỘT CHÚT YÊU THƯƠNG</span><h2 id="modal-title">{{ {jar:'Một hũ mới',memory:'Lưu lại khoảnh khắc',event:'Một ngày đặc biệt',profile:'Hồ sơ của bạn'}[modal] }} ♡</h2><p v-if="error" class="alert" role="alert">{{ error }}</p><form @submit.prevent="save">
      <template v-if="modal === 'profile'"><label>Tên hiển thị<input v-model="form.display_name" required maxlength="100"></label><label>Ngày sinh<input type="date" v-model="form.birth_date"></label><label>Giới tính<select v-model="form.gender"><option value="">Không chia sẻ</option><option>Nam</option><option>Nữ</option><option>Khác</option></select></label><label>Giới thiệu<textarea v-model="form.bio" maxlength="120"></textarea></label></template>
      <template v-else><label>{{ modal === 'jar' ? 'Tên hũ' : 'Tiêu đề' }}<input v-if="modal === 'jar'" v-model="form.name" required maxlength="100" placeholder="Ví dụ: Những buổi hẹn hò"><input v-else v-model="form.title" required maxlength="150" placeholder="Một điều mình muốn nhớ…"></label><label v-if="modal !== 'jar'">Ngày<input v-model="form.date" type="date" required></label><div class="emoji-picker"><button v-for="e in emojis" type="button" :class="{chosen: form.emoji === e}" @click="form.emoji = e">{{ e }}</button></div><label v-if="modal === 'jar'">Màu chiếc hũ<input type="color" v-model="form.color"></label><template v-if="modal === 'memory'"><label>Chọn hũ<select v-model="form.jar" required :disabled="!!form.id"><option v-for="j in jars" :value="j.id">{{ j.emoji }} {{ j.name }}</option></select></label><label>Câu chuyện của chúng ta<textarea v-model="form.story" maxlength="5000" placeholder="Hôm ấy có điều gì dễ thương?"></textarea></label><label class="upload"><Camera :size="24"/> Thêm ảnh (JPEG, PNG, WebP · tối đa 10 MB/ảnh)<input type="file" accept="image/jpeg,image/png,image/webp" multiple :disabled="!!form.id" @change="files = Array.from($event.target.files)"><small>{{ files.length }} ảnh chờ tải lên</small></label><p v-if="form.id">Kỷ niệm đã được lưu. Bấm lưu lại để thử tải các ảnh còn lại.</p></template></template>
      <button class="primary" :disabled="busy">{{ busy ? 'Đang lưu…' : 'Lưu vào Tủ thương ♡' }}</button></form></section></div>
    <div v-if="detail" class="modal-backdrop" @click.self="detail = null"><section class="modal memory-detail" role="dialog" aria-modal="true" aria-label="Chi tiết kỷ niệm"><button class="close icon-button" @click="detail = null" aria-label="Đóng"><X/></button><small>{{ detail.date }} · {{ detail.author_name }}</small><h2>{{ detail.emoji }} {{ detail.title }}</h2><div class="detail-photos"><PrivatePhoto v-for="photo in detail.photos" :key="photo.id" :url="photo.url"/></div><p class="story">{{ detail.story }}</p><button class="secondary" @click="react" :disabled="busy"><Heart :fill="detail.liked ? 'currentColor' : 'none'" :size="18"/> {{ detail.likes }} yêu thương</button><hr><h3>Lời nhắn của chúng ta</h3><div v-for="c in detail.comments" class="comment"><strong>{{ c.author_name }}</strong><p>{{ c.text }}</p></div><form @submit.prevent="addComment" class="comment-form"><input v-model="comment" required maxlength="1000" placeholder="Để lại một lời nhắn…"><button class="primary" :disabled="busy"><MessageCircle :size="18"/> Gửi</button></form><button class="text-button danger" @click="remove('memories', detail.id)">Xóa kỷ niệm</button><p v-if="error" class="alert" role="alert">{{ error }}</p></section></div>
  </div>
</template>
