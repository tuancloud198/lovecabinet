<script setup>
// Đố vui: each partner writes multiple-choice questions about themselves; the other answers them.
// Every answer gives the pet QUIZ_POINTS; answering on consecutive days (either of us) builds the streak.
import { ref, computed } from 'vue'
import { Check, Flame, Plus, RefreshCw, Star, Trophy, X } from 'lucide-vue-next'
import { api } from '@/api.js'
import { QUIZ_POINTS } from '@/characters.js'
import { isoDate, timeAgo } from '@/format.js'
import { QUESTION_BANK } from '@/quizBank.js'
import { state, partner, run, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import DailyPoints from '@/components/DailyPoints.vue'
import QuizBattle from '@/components/QuizBattle.vue'

const LETTERS = ['A', 'B', 'C', 'D']
const me = computed(() => state.me.id)
const partnerName = computed(() => partner.value?.display_name || 'người ấy')
const petName = computed(() => state.couple.pet_name)
const byOldest = (a, b) => a.id - b.id
const waiting = computed(() => state.quiz.filter(q => q.author !== me.value && !q.answer).sort(byOldest))
const asked = computed(() => state.quiz.filter(q => q.author === me.value).sort((a, b) => b.id - a.id))
const answered = computed(() => state.quiz.filter(q => q.author !== me.value && q.answer).sort((a, b) => b.answer.created_at.localeCompare(a.answer.created_at)))
const answeredToday = computed(() => state.quiz.some(q => q.answer?.answered_on === isoDate()))
const tab = ref('waiting') // waiting | asked | answered

// ---- Answering ----
const current = ref(null) // the question being answered
const result = ref(null) // { question, points } after answering
function openAnswer(question) {
  result.value = null
  current.value = question
  state.error = ''
}
function choose(index) {
  run(async () => {
    const data = await api(`quiz-questions/${current.value.id}/answer/`, { method: 'POST', body: { choice: index } })
    state.quiz = state.quiz.map(q => (q.id === data.question.id ? data.question : q))
    Object.assign(state.couple, { quiz_streak: data.streak, quiz_max_streak: data.max_streak, points_earned: (state.couple.points_earned || 0) + data.points, points_today: (state.couple.points_today || 0) + data.points })
    result.value = { question: data.question, points: data.points }
  })
}
function nextQuestion() {
  const next = waiting.value[0]
  if (next) openAnswer(next)
  else closeAnswer()
}
function closeAnswer() { current.value = null; result.value = null }
const choiceClass = (question, index) => {
  if (!question.answer) return ''
  if (index === question.correct) return 'right'
  return index === question.answer.choice ? 'wrong' : ''
}

// ---- Writing questions ----
const writing = ref(false)
const form = ref(null)
const suggestions = ref([])
const shuffle = () => { suggestions.value = [...QUESTION_BANK].sort(() => Math.random() - 0.5).slice(0, 5) }
function startWriting() {
  form.value = { text: '', choices: ['', ''], correct: 0 }
  shuffle()
  state.error = ''
  writing.value = true
}
function addChoice() { if (form.value.choices.length < 4) form.value.choices.push('') }
function removeChoice(index) {
  form.value.choices.splice(index, 1)
  if (form.value.correct >= form.value.choices.length) form.value.correct = 0
  else if (form.value.correct > index) form.value.correct--
}
function saveQuestion(another) {
  run(async () => {
    const body = { text: form.value.text.trim(), choices: form.value.choices.map(c => c.trim()), correct: form.value.correct }
    state.quiz = [await api('quiz-questions/', { method: 'POST', body }), ...state.quiz]
    toast(`Đã gửi câu đố cho ${partnerName.value}!`)
    if (another) startWriting()
    else { writing.value = false; tab.value = 'asked' }
  })
}
function removeQuestion(question) {
  if (!window.confirm('Xóa câu đố này?')) return
  run(async () => {
    await api(`quiz-questions/${question.id}/`, { method: 'DELETE' })
    state.quiz = state.quiz.filter(q => q.id !== question.id)
  })
}
</script>

<template>
  <div class="page quiz-page">
    <AppHeader title="Đố vui" />

    <QuizBattle />
    <section class="quiz-stats">
      <div class="quiz-stat streak" :class="{ lit: answeredToday }">
        <Flame :size="22" /><strong>{{ state.couple.quiz_streak || 0 }}</strong><small>ngày liên tiếp</small>
      </div>
      <div class="quiz-stat"><Trophy :size="22" /><strong>{{ state.couple.quiz_max_streak || 0 }}</strong><small>kỷ lục</small></div>
      <div class="quiz-stat"><Star :size="22" /><strong>{{ state.couple.points_earned || 0 }}</strong><small>điểm cho {{ petName }}</small></div>
    </section>
    <DailyPoints />
    <p class="muted center quiz-hint">{{ answeredToday ? 'Hôm nay đã giữ chuỗi rồi 🔥' : 'Trả lời một câu hôm nay để giữ chuỗi nhé!' }}</p>

    <div class="segmented quiz-tabs" role="tablist">
      <button role="tab" :aria-selected="tab === 'waiting'" :class="{ active: tab === 'waiting' }" @click="tab = 'waiting'">Cho bạn<span v-if="waiting.length" class="quiz-count">{{ waiting.length }}</span></button>
      <button role="tab" :aria-selected="tab === 'asked'" :class="{ active: tab === 'asked' }" @click="tab = 'asked'">Bạn đã ra</button>
      <button role="tab" :aria-selected="tab === 'answered'" :class="{ active: tab === 'answered' }" @click="tab = 'answered'">Đã trả lời</button>
    </div>

    <section v-if="tab === 'waiting'" class="quiz-list">
      <p v-if="!waiting.length" class="muted center">Chưa có câu đố mới từ {{ partnerName }}. Ra đề cho người ấy trước nhé!</p>
      <button v-for="q in waiting" :key="q.id" class="quiz-card card" @click="openAnswer(q)">
        <span class="quiz-q">{{ q.text }}</span>
        <small class="muted">{{ q.author_name }} · {{ timeAgo(q.created_at) }} · {{ q.choices.length }} lựa chọn</small>
        <span class="chip">Trả lời · +{{ QUIZ_POINTS }} điểm</span>
      </button>
    </section>

    <section v-else-if="tab === 'asked'" class="quiz-list">
      <p v-if="!asked.length" class="muted center">Bạn chưa ra câu nào. Bấm + để đố {{ partnerName }} nhé!</p>
      <div v-for="q in asked" :key="q.id" class="quiz-card card">
        <span class="quiz-q">{{ q.text }}</span>
        <ol class="quiz-choices small">
          <li v-for="(c, i) in q.choices" :key="i" :class="[choiceClass(q, i), { key: !q.answer && i === q.correct }]"><b>{{ LETTERS[i] }}</b>{{ c }}</li>
        </ol>
        <div class="quiz-status">
          <small v-if="!q.answer" class="muted">Đang chờ {{ partnerName }} trả lời…</small>
          <small v-else :class="q.answer.correct ? 'ok' : 'bad'">{{ partnerName }} chọn {{ LETTERS[q.answer.choice] }} · {{ q.answer.correct ? 'Đúng rồi! 🎉' : 'Sai mất rồi 😝' }}</small>
          <button v-if="!q.answer" class="icon-button" aria-label="Xóa câu đố" @click="removeQuestion(q)"><X :size="16" /></button>
        </div>
      </div>
    </section>

    <section v-else class="quiz-list">
      <p v-if="!answered.length" class="muted center">Bạn chưa trả lời câu nào.</p>
      <div v-for="q in answered" :key="q.id" class="quiz-card card">
        <span class="quiz-q">{{ q.text }}</span>
        <ol class="quiz-choices small">
          <li v-for="(c, i) in q.choices" :key="i" :class="choiceClass(q, i)"><b>{{ LETTERS[i] }}</b>{{ c }}</li>
        </ol>
        <small :class="q.answer.correct ? 'ok' : 'bad'">{{ q.answer.correct ? 'Bạn trả lời đúng! 🎉' : 'Bạn trả lời sai 😝' }} · {{ timeAgo(q.answer.created_at) }}</small>
      </div>
    </section>

    <button class="fab" aria-label="Ra câu đố mới" @click="startWriting"><Plus :size="26" /></button>

    <!-- Answer a question -->
    <BottomSheet v-if="current" :title="`${current.author_name} đố bạn ♡`" @close="closeAnswer">
      <div class="stack">
        <p class="quiz-q big">{{ (result?.question || current).text }}</p>
        <div class="quiz-options">
          <button v-for="(c, i) in (result?.question || current).choices" :key="i" class="quiz-option" :class="result ? choiceClass(result.question, i) : ''" :disabled="state.busy || !!result" @click="choose(i)">
            <b>{{ LETTERS[i] }}</b><span>{{ c }}</span>
            <Check v-if="result && i === result.question.correct" :size="18" /><X v-else-if="result && i === result.question.answer.choice" :size="18" />
          </button>
        </div>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <template v-if="result">
          <p class="quiz-result" :class="result.question.answer.correct ? 'ok' : 'bad'">
            {{ result.question.answer.correct ? 'Chính xác! Bạn hiểu người ấy ghê 🎉' : `Chưa đúng rồi, đáp án là ${LETTERS[result.question.correct]} 😝` }}
          </p>
          <p class="muted center">{{ result.points ? `+${result.points} điểm cho ${petName}` : 'Hôm nay đã đủ điểm rồi' }} · chuỗi {{ state.couple.quiz_streak }} ngày 🔥</p>
          <button class="btn primary block" @click="nextQuestion">{{ waiting.length ? `Câu tiếp theo (${waiting.length})` : 'Xong' }}</button>
        </template>
      </div>
    </BottomSheet>

    <!-- Write a question -->
    <BottomSheet v-if="writing" :title="`Đố ${partnerName} ♡`" @close="writing = false">
      <form class="stack" @submit.prevent="saveQuestion(false)">
        <div class="field"><span>Gợi ý</span>
          <div class="quiz-suggestions">
            <button v-for="s in suggestions" :key="s" type="button" class="chip soft" @click="form.text = s">{{ s }}</button>
            <button type="button" class="chip soft" aria-label="Đổi gợi ý" @click="shuffle"><RefreshCw :size="14" /></button>
          </div>
        </div>
        <label class="field">Câu hỏi<input v-model="form.text" required maxlength="200" placeholder="Món ăn mình thích nhất là gì?" /></label>
        <fieldset class="field"><legend>Các lựa chọn <span class="muted">(chạm chữ cái để chọn đáp án đúng)</span></legend>
          <div v-for="(c, i) in form.choices" :key="i" class="quiz-edit-choice">
            <button type="button" class="quiz-letter" :class="{ chosen: form.correct === i }" :aria-label="`Đáp án đúng là ${LETTERS[i]}`" :aria-pressed="form.correct === i" @click="form.correct = i">{{ LETTERS[i] }}</button>
            <input v-model="form.choices[i]" required maxlength="100" :placeholder="`Lựa chọn ${LETTERS[i]}`" :aria-label="`Lựa chọn ${LETTERS[i]}`" />
            <button v-if="form.choices.length > 2" type="button" class="icon-button" :aria-label="`Bỏ lựa chọn ${LETTERS[i]}`" @click="removeChoice(i)"><X :size="16" /></button>
          </div>
          <button v-if="form.choices.length < 4" type="button" class="btn outline small" @click="addChoice"><Plus :size="16" /> Thêm lựa chọn</button>
        </fieldset>
        <p class="muted quiz-hint">Đáp án đúng: <strong>{{ LETTERS[form.correct] }}</strong> · {{ partnerName }} sẽ không thấy đáp án cho đến khi trả lời.</p>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Gửi câu đố</button>
        <button type="button" class="btn tertiary block" :disabled="state.busy" @click="$event.target.form.reportValidity() && saveQuestion(true)">Gửi & ra câu khác</button>
      </form>
    </BottomSheet>
  </div>
</template>
