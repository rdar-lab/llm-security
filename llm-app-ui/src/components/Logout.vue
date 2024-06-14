<template>
  <a href="#" @click="handleLogout()">Logout</a>
</template>

<script setup>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const handleLogout = () => {
  store.dispatch('auth/logout')
      .then(() => {
        router.push('/login')
      })
      .catch((error) => {
            console.error(error)
            alert('An error occurred during logout.')
          }
      )
}


</script>