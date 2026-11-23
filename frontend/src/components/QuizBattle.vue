<script setup>
// Đố vui scoreboard, head to head: who understands the other better. For each of us: questions
// answered, answered correctly, and the correct rate. Whoever has more correct answers leads (the
// rate breaks a tie); the tug-of-war bar shows the split of correct answers.
import { computed } from 'vue'
import { Swords } from 'lucide-vue-next'
import { state, partner } from '@/store.js'
import CharacterAvatar from '@/components/CharacterAvatar.vue'

function score(user) {
  const answers = state.quiz.filter(q => q.answer && q.answer.user === user?.id)
  const correct = answers.filter(q => q.answer.correct).length
  return { user, answered: answers.length, correct, rate: answers.length ? Math.round((correct / answers.length) * 100) : 0 }
}
const me = computed(() => score(state.me))
const them = computed(() => score(partner.value))
const lead = computed(() => Math.sign(me.value.correct - them.value.correct || me.value.rate - them.value.rate)) // 1 me, -1 them, 0 tie
const myShare = computed(() => {
  const total = me.value.correct + them.value.correct
  return total ? Math.round((me.value.correct / total) * 100) : 50
})
const shout = computed(() => {
  if (!me.value.answered && !them.value.answered) return 'Chưa ai ra trận. Ra đề đầu tiên nào! ⚔️'
  const gap = Math.abs(me.value.correct - them.value.correct)
  if (lead.value === 0) return 'Ngang tài ngang sức! 🤝'
  const leader = lead.value > 0 ? 'Bạn' : (partner.value?.display_name || 'Người ấy')
  return gap ? `${leader} đang dẫn trước ${gap} câu! 🔥` : `${leader} dẫn trước nhờ tỉ lệ đúng cao hơn! 🔥`
})
const ROWS = [
  { key: 'rate', label: 'Tỉ lệ đúng', unit: '%' },
  { key: 'answered', label: 'Đã trả lời', unit: '' },
  { key: 'correct', label: 'Trả lời đúng', unit: '' },
]
const better = (key, side) => {
  const [a, b] = side === 'me' ? [me.value[key], them.value[key]] : [them.value[key], me.value[key]]
  return a > b
}
</script>

<template>
  <section class="battle" aria-label="Bảng đấu: ai hiểu ai hơn">
    <h2 class="battle-title"><Swords :size="18" /> Ai hiểu ai hơn? <Swords :size="18" /></h2>
    <div class="battle-fighters">
      <div class="fighter" :class="{ leader: lead > 0, loser: lead < 0 }">
        <span class="crown" aria-hidden="true">{{ lead > 0 ? '👑' : '' }}</span>
        <CharacterAvatar :user="state.me" :mood="lead > 0 ? 'excited' : lead < 0 ? 'shy' : 'happy'" :size="64" />
        <strong>Bạn</strong>
      </div>
      <span class="battle-vs" aria-hidden="true">VS</span>
      <div class="fighter" :class="{ leader: lead < 0, loser: lead > 0 }">
        <span class="crown" aria-hidden="true">{{ lead < 0 ? '👑' : '' }}</span>
        <CharacterAvatar :user="partner" :mood="lead < 0 ? 'excited' : lead > 0 ? 'shy' : 'happy'" :size="64" />
        <strong>{{ partner?.display_name || 'Người ấy' }}</strong>
      </div>
    </div>
    <dl class="battle-rows">
      <div v-for="row in ROWS" :key="row.key" class="battle-row">
        <dd :class="{ win: better(row.key, 'me') }">{{ me[row.key] }}{{ row.unit }}</dd>
        <dt>{{ row.label }}</dt>
        <dd :class="{ win: better(row.key, 'them') }">{{ them[row.key] }}{{ row.unit }}</dd>
      </div>
    </dl>
    <div class="battle-bar" role="img" :aria-label="`Câu đúng: bạn ${me.correct}, ${partner?.display_name || 'người ấy'} ${them.correct}`">
      <span class="battle-bar-me" :style="{ width: myShare + '%' }"></span>
      <span class="battle-bar-knot" :style="{ left: myShare + '%' }">⚡</span>
    </div>
    <p class="battle-shout">{{ shout }}</p>
  </section>
</template>
