<script setup>
import { RouterLink } from 'vue-router'
import Logout from './Logout.vue'
import Protector from './Protector.vue'
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])

</script>

<template>
  <header v-if="isAuthenticated">
    <div class="wrapper">
      <nav>
        <RouterLink to="/txManager">Tx-Manager</RouterLink>
        <RouterLink to="/siteInfo">Site-Info</RouterLink>
        <Logout />
        <Protector />
      </nav>
    </div>
  </header>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

nav {
  width: 100%;
  font-size: 14px;
  text-align: center;
  margin-top: 2rem;
  padding: 1rem 0;
}

nav a.router-link-exact-active {
  color: #495057;
  font-weight: bold;
}

nav a.router-link-exact-active:hover {
  background-color: #f8f9fa;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid #dee2e6;
  color: #6c757d;
  text-decoration: none;
}

nav a:first-of-type {
  border: 0;
}


</style>