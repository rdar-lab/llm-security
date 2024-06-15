<template>
  <div class="site-view">
    <h1 class="title">Ask a question on a site</h1>
    <form @submit.prevent="askQuestion">
      <label for="mode">Mode:</label>
      <select id="mode" v-model="question.mode" required>
        <option v-for="option in modeOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <label for="url">Site URL:</label>
      <input id="url" v-model="question.siteUrl" type="text" required placeholder="http://....">

      <label for="question">Question:</label>
      <textarea id="question" v-model="question.query" required placeholder="Summarize this site"></textarea>

      <button type="submit" :disabled="isLoading">
        <span>Ask</span>
        <span v-if="isLoading" class="spinner"></span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex'

import Swal from "sweetalert2";
import { showAIResponse } from "@/utils/AiUtils.js";

const store = useStore()

const question = ref({ mode: 'rag', siteUrl: '', query: '' })

const modeOptions = [
  { value: 'rag', label: 'RAG' },
  { value: 'retriever', label: 'Retriever' },
  { value: 'retriever-embedding', label: 'Retriever - With Embedding' },
]

const isLoading = ref(false)

const askQuestion = () => {
  isLoading.value = true
  store.dispatch('site/askQuestion', question.value)
      .then(async (response) => {
        await showAIResponse(response);
      })
      .catch(async error => {
        console.log(error);
        await Swal.fire('Error', "Failed to ask question: " + error, 'error')
      })
      .then(() => {
        isLoading.value = false
      })
}

</script>

<style scoped>
.site-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
  background-color: #f0f0f0;
  padding: 2rem;
  box-sizing: border-box;
}

.title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 2rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 1000px;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

label {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

input {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

textarea {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

button {
  align-self: flex-end;
  padding: 0.5rem 1rem;
  background-color: #007BFF;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.spinner {
  display: inline-block;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  animation: spin 2s linear infinite;
  vertical-align: middle;
  margin-left: 5px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>