<template>
  <select v-model="selectedProtector"  class="protection-mode">
    <option v-for="(value, key) in protectors" :value="key">{{ value }}</option>
  </select>
</template>

<script setup>
import { computed, ref, onMounted, watch } from "vue";
import { useStore } from 'vuex'
const store = useStore()

const protectors = computed(() => store.getters['protections/getProtectors'])
const selectedProtectorFromStore = computed(() => store.getters['protections/selectedProtector'])
const selectedProtector = ref('')
onMounted(() => {
  selectedProtector.value = selectedProtectorFromStore.value
})
watch(selectedProtectorFromStore, (newVal) => {
  selectedProtector.value = newVal
})
watch(selectedProtector, (newVal) => {
  store.commit('protections/setSelectedProtector', { selectedProtector: newVal })
})

</script>

<style scoped>

.protection-mode {
  float: right;
  border: 1px solid #ccc;
  padding: 5px 5px 5px 10px;
  font-size: 16px;
  color: #333;
  background-color: #fff;
  transition: background-color 0.3s ease;
}

.protection-mode:hover {
  background-color: #f8f9fa;
}

</style>