<template>
  <div>
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
          <td>{{ transaction.date }}</td>
          <td>{{ transaction.amount }}</td>
          <td>{{ transaction.description }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="transaction-form">
      <form @submit.prevent="addTransaction">
        <input v-model="newTransaction.amount" type="number" placeholder="Amount" required>
        <input v-model="newTransaction.description" type="text" placeholder="Description" required>
        <button type="submit">Add Transaction</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const refreshTransactions = () => {
  store.dispatch('transactions/refreshTransactions')
}

onMounted(refreshTransactions)

const transactions = computed(() => store.getters['transactions/transactions'])

const newTransaction = ref({ amount: 0, description: '' })

const addTransaction = () => {
  store.dispatch('transactions/addTransaction', {transaction: newTransaction.value})
      .then(() => {
        refreshTransactions()
        newTransaction.value = { amount: 0, description: '' }
      })
      .catch(error => {
        alert("Failed to add transaction: "+ error);
      })
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

.alternate-row {
  background-color: #f2f2f2;
}

.transaction-form {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #f2f2f2;
  padding: 20px;
  box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.1);
}

.transaction-form form {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transaction-form input {
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
</style>