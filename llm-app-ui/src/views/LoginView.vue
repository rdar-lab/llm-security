<template>
  <div class="login-view">
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

const username = ref('')
const password = ref('')
const store = useStore()
const router = useRouter()


const handleSubmit = () => {
  const payload = { username: username.value, password: password.value }
  store.dispatch('auth/login', payload)
      .then(() => {
        router.push('/siteInfo')
      })
      .catch((error) => {
            console.error(error)
            alert('An error occurred during login.')
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
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

button {
  align-self: flex-end;
}
</style>