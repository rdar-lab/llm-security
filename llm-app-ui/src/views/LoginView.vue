<template>
  <div class="login-view">
    <h1 class="title">Login to Your Account</h1>
    <form @submit.prevent="handleSubmit">
      <label for="username">Username:</label>
      <input id="username" v-model="username" type="text" required>

      <label for="password">Password:</label>
      <input id="password" v-model="password" type="password" required>

      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import Swal from "sweetalert2";

const username = ref('')
const password = ref('')
const store = useStore()
const router = useRouter()


const handleSubmit = () => {
  const payload = { username: username.value, password: password.value }
  store.dispatch('auth/login', payload)
      .then(() => {
        router.push('/txManager')
      })
      .catch(async (error) => {
            console.error(error)
            await Swal.fire('Access Denied', 'Invalid username or password', 'error')
          }
      )
}

</script>

<style scoped>
.login-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
  max-width: 400px;
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
</style>