<script setup>
// Edit our two dates: the day we first met and the day we started loving each other.
import { ref, computed } from 'vue'
import { api } from '@/api.js'
import { daysTogether } from '@/anniversaries.js'
import { isoDate } from '@/format.js'
import { state, run, toast } from '@/store.js'
import BottomSheet from '@/components/BottomSheet.vue'

const emit = defineEmits(['close'])
const today = isoDate()
const form = ref({ met_on: state.couple.met_on || '', dating_since: state.couple.dating_since || '' })
const days = computed(() => daysTogether({ dating_since: form.value.dating_since || null }))
state.error = ''

function save() {
  run(async () => {
    const body = { met_on: form.value.met_on || null, dating_since: form.value.dating_since || null }
    state.couple = await api(`couples/${state.couple.id}/`, { method: 'PATCH', body })
    toast('Đã lưu ngày của chúng mình ♡')
    emit('close')
  })
}
</script>

<template>
  <BottomSheet title="Ngày của chúng mình ♡" @close="emit('close')">
    <form class="stack" @submit.prevent="save">
      <label class="field">👋 Ngày gặp nhau lần đầu<input v-model="form.met_on" type="date" :max="form.dating_since || today" /></label>
      <label class="field">💘 Ngày bắt đầu yêu nhau<input v-model="form.dating_since" type="date" :min="form.met_on || undefined" :max="today" /></label>
      <p v-if="days" class="muted center">Hôm nay là ngày thứ <strong class="heart">{{ days }}</strong> hai bạn yêu nhau.</p>
      <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
      <button class="btn primary block" :disabled="state.busy">Lưu</button>
    </form>
  </BottomSheet>
</template>
