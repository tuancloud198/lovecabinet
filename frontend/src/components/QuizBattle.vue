<script setup>
// Đố vui scoreboard, head to head: who understands the other better. For each of us: questions
// answered, answered correctly, and the correct rate. Whoever has more correct answers leads (the
// rate breaks a tie); the tug-of-war bar shows the split of correct answers, with the pet as the knot.
import { computed } from 'vue'
import { Crown, Heart } from 'lucide-vue-next'
import { state, partner } from '@/store.js'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import EmojiIcon from '@/components/EmojiIcon.vue'
import PetArt from '@/components/PetArt.vue'

function score(user) {
  const answers = state.quiz.filter(q => q.answer && q.answer.user === user?.id)
  const correct = answers.filter(q => q.answer.correct).length
  return { user, answered: answers.length, correct, rate: answers.length ? Math.round((correct / answers.length) * 100) : 0 }
}
const me = computed(() => score(state.me))
const them = computed(() => score(partner.value))
const partnerName = computed(() => partner.value?.display_name || 'Người ấy')
const lead = computed(() => Math.sign(me.value.correct - them.value.correct || me.value.rate - them.value.rate)) // 1 me, -1 them, 0 tie
const myShare = computed(() => {
  const total = me.value.correct + them.value.correct
  return total ? Math.round((me.value.correct / total) * 100) : 50
})
const shout = computed(() => {
  if (!me.value.answered && !them.value.answered) return 'Chưa ai trả lời câu nào. Ra đề đầu tiên nhé! 💌'
  const gap = Math.abs(me.value.correct - them.value.correct)
  if (lead.value === 0) return 'Hai bạn hiểu nhau ngang ngửa luôn! 💞'
  const leader = lead.value > 0 ? 'Bạn' : partnerName.value
  return gap ? `${leader} đang dẫn trước ${gap} câu nè! 💕` : `${leader} dẫn trước nhờ tỉ lệ đúng cao hơn nè! 💕`
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
    <h2 class="battle-title">Ai hiểu ai hơn? <Heart class="battle-title-heart" :size="16" fill="currentColor" aria-hidden="true" /></h2>
    <div class="battle-fighters">
      <div class="fighter me" :class="{ leader: lead > 0 }">
        <span class="fighter-pic">
          <CharacterAvatar :user="state.me" :mood="lead > 0 ? 'excited' : lead < 0 ? 'shy' : 'happy'" :size="64" />
          <span v-if="lead > 0" class="crown" aria-hidden="true"><Crown :size="14" :stroke-width="2.5" /></span>
        </span>
        <strong>Bạn</strong>
      </div>
      <span class="battle-vs" aria-hidden="true"><EmojiIcon emoji="❤️" /><small>vs</small></span>
      <div class="fighter them" :class="{ leader: lead < 0 }">
        <span class="fighter-pic">
          <CharacterAvatar :user="partner" :mood="lead < 0 ? 'excited' : lead > 0 ? 'shy' : 'happy'" :size="64" />
          <span v-if="lead < 0" class="crown" aria-hidden="true"><Crown :size="14" :stroke-width="2.5" /></span>
        </span>
        <strong>{{ partnerName }}</strong>
      </div>
    </div>
    <dl class="battle-rows">
      <div v-for="row in ROWS" :key="row.key" class="battle-row">
        <dd class="me" :class="{ win: better(row.key, 'me') }">{{ me[row.key] }}{{ row.unit }}</dd>
        <dt>{{ row.label }}</dt>
        <dd class="them" :class="{ win: better(row.key, 'them') }">{{ them[row.key] }}{{ row.unit }}</dd>
      </div>
    </dl>
    <div class="battle-bar" role="img" :aria-label="`Câu đúng: bạn ${me.correct}, ${partnerName} ${them.correct}`">
      <span class="battle-bar-track"><span class="battle-bar-me" :style="{ width: myShare + '%' }"></span></span>
      <span class="battle-bar-knot" :style="{ left: `clamp(20px, ${myShare}%, calc(100% - 20px))` }"><PetArt mood="happy" face /></span>
    </div>
    <p class="battle-shout">{{ shout }}</p>
  </section>
</template>
