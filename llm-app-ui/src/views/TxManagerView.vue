<template>
  <div>
    <div class="question-form">
      <form @submit.prevent="askQuestion">
        <select v-model="question.mode" required>
          <option v-for="option in modeOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <input v-model="question.query" type="text" placeholder="Ask a question (Example: What is my balance?)"
               required>
        <button type="submit" :disabled="isLoading">
          <span>Ask</span>
          <span v-if="isLoading" class="spinner"></span>
        </button>
      </form>
    </div>

    <div class="table-container">
      <table class="styled-table">
        <thead>
        <tr>
          <th>Date</th>
          <th>Amount</th>
          <th>Description</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="transaction in transactions" :key="transaction.created_at">
          <td class="date-column">{{ formatDate(transaction.date) }}</td>
          <td class="amount-column">{{ transaction.amount }}</td>
          <td>{{ transaction.description }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="transaction-form">
      <form @submit.prevent="addTransaction">
        <input v-model="newTransaction.amount" type="number" placeholder="Amount" required class="amount-input">
        <input v-model="newTransaction.description" type="text" placeholder="Description" required class="desc-input">
        <button type="submit">Add Transaction</button>
      </form>
    </div>
  </div>

</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import Swal from 'sweetalert2'
import { showAIResponse } from "@/utils/AiUtils.js";

const store = useStore()

const refreshTransactions = () => {
  store.dispatch('transactions/refreshTransactions')
}

onMounted(refreshTransactions)

const transactions = computed(() => store.getters['transactions/transactions'])

const newTransaction = ref({ amount: 0, description: '' })

const addTransaction = () => {
  store.dispatch('transactions/addTransaction', { transaction: newTransaction.value })
      .then(() => {
        refreshTransactions()
        newTransaction.value = { amount: 0, description: '' }
      })
      .catch(error => {
        alert("Failed to add transaction: " + error);
      })
}

const question = ref({ mode: 'rag', query: '' })

const modeOptions = [
  { value: 'rag', label: 'RAG' },
  { value: 'sql', label: 'Gen-SQL' },
  { value: 'preloaded', label: 'Pre-Load' },
]

const isLoading = ref(false)

const askQuestion = () => {
  isLoading.value = true
  store.dispatch('transactions/askQuestion', { mode: question.value.mode, query: question.value.query })
      .then(async (response) => {
        await showAIResponse(response);
      })
      .catch(async error => {
        await Swal.fire('Error', "Failed to ask question: " + error, 'error')
      })
      .then(() => {
        isLoading.value = false
      })
}

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed in JavaScript
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

</script>
<style scoped>
.table-container {
  padding-bottom: 100px;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
}

.styled-table th,
.styled-table td {
  border: 1px solid #ddd;
  padding: 8px;
}

.styled-table th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #3e4340;
  color: white;
}

.transaction-form {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #f2f2f2;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.transaction-form form {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-input {
  flex: 0.3;
  margin-right: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.desc-input {
  flex: 1;
  margin-right: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.transaction-form button {
  margin-right: 50px;
  padding: 10px 20px;
  border: none;
  background-color: #3e4340;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

.question-form {
  background-color: #f2f2f2;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.question-form form {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-form input {
  flex: 1;
  margin-right: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}


.question-form select {
  margin-right: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.question-form button {
  margin-right: 50px;
  padding: 10px 20px;
  border: none;
  background-color: #3e4340;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

.date-column {
  width: 300px;
}

.amount-column {
  width: 150px;
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