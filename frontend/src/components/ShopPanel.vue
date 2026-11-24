<script setup>
// Cửa hàng: spend the couple's points (the same points the pet grows with) on items. Spending only
// lowers the shop balance; the pet keeps every point it earned. Items are shared by the couple;
// each partner picks their own theme.
import { computed } from 'vue'
import { Check, Lock, ShoppingBag } from 'lucide-vue-next'
import { api } from '@/api.js'
import { state, run, toast } from '@/store.js'

// Colours shown on each theme's card (its primary, light, page and wood colours).
const SWATCHES = {
  '': ['#B9473E', '#FBE5DD', '#F6E8DD', '#E2B988'],
  pink: ['#C94F7C', '#FCE4EE', '#F9E1EA', '#F2C1D1'],
}
const shop = computed(() => state.shop || { earned: 0, spent: 0, balance: 0, items: [] })
const themeOf = item => item.id.replace(/^theme_/, '')
const myTheme = computed(() => state.me.theme || '')
const pet = computed(() => state.couple.pet_name)

function buy(item) {
  if (!window.confirm(`Mua "${item.name}" với ${item.price} điểm?`)) return
  run(async () => {
    state.shop = await api(`shop/${item.id}/buy/`, { method: 'POST' })
    toast(`Đã mua "${item.name}"! ♡`)
    if (item.kind === 'theme') await useTheme(themeOf(item))
  })
}
async function useTheme(theme) {
  state.me = await api('users/me/', { method: 'PATCH', body: { theme } })
  const member = state.couple.members.find(m => m.id === state.me.id)
  if (member) Object.assign(member, state.me)
}
function apply(theme) {
  run(async () => { await useTheme(theme); toast(theme ? 'Đã đổi giao diện!' : 'Đã dùng giao diện mặc định.') })
}
</script>

<template>
  <section class="shop">
    <div class="wallet card">
      <span class="wallet-icon"><ShoppingBag :size="22" /></span>
      <div class="wallet-main"><small>Điểm cửa hàng</small><strong>{{ shop.balance }}</strong></div>
      <small class="wallet-detail">Đã kiếm {{ shop.earned }} · đã tiêu {{ shop.spent }}<br />Mua sắm không trừ điểm của {{ pet }} đâu nhé!</small>
    </div>

    <h3 class="subhead">Giao diện</h3>
    <div class="shop-grid">
      <div class="shop-item card" :class="{ active: myTheme === '' }">
        <span class="theme-swatches"><i v-for="c in SWATCHES['']" :key="c" :style="{ background: c }"></i></span>
        <strong>Mặc định</strong><small class="muted">Nâu ấm như tủ gỗ.</small>
        <button class="btn small block" :class="myTheme === '' ? 'tertiary' : 'outline'" :disabled="state.busy || myTheme === ''" @click="apply('')">
          <template v-if="myTheme === ''"><Check :size="16" /> Đang dùng</template><template v-else>Dùng</template>
        </button>
      </div>
      <div v-for="item in shop.items.filter(i => i.kind === 'theme')" :key="item.id" class="shop-item card" :class="{ active: myTheme === themeOf(item) }">
        <span class="theme-swatches"><i v-for="c in SWATCHES[themeOf(item)] || []" :key="c" :style="{ background: c }"></i></span>
        <strong>{{ item.name }}</strong><small class="muted">{{ item.description }}</small>
        <button v-if="!item.owned" class="btn primary small block" :disabled="state.busy || shop.balance < item.price" @click="buy(item)">Mua · {{ item.price }} điểm</button>
        <button v-else class="btn small block" :class="myTheme === themeOf(item) ? 'tertiary' : 'outline'" :disabled="state.busy || myTheme === themeOf(item)" @click="apply(themeOf(item))">
          <template v-if="myTheme === themeOf(item)"><Check :size="16" /> Đang dùng</template><template v-else>Dùng</template>
        </button>
        <small v-if="!item.owned && shop.balance < item.price" class="muted center">Còn thiếu {{ item.price - shop.balance }} điểm</small>
      </div>
    </div>

    <h3 class="subhead">Bạn nhỏ mới</h3>
    <div class="shop-grid">
      <div class="shop-item card soon">
        <span class="shop-soon-art">🐱</span>
        <strong>Mèo</strong><small class="muted">Sắp có trong cửa hàng.</small>
        <button class="btn small block outline" disabled><Lock :size="14" /> Sắp có</button>
      </div>
    </div>
    <p class="muted center shop-hint">Mỗi kỷ niệm +10 điểm · mỗi câu đố được trả lời +2 điểm.</p>
  </section>
</template>
