import { createRouter, createWebHistory } from 'vue-router'
import SiteInfoView from '../views/SiteInfoView.vue'
import TxManagerView from '../views/TxManagerView.vue'
import LoginView from "@/views/LoginView.vue";
import store from "@/store/store.js";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/siteInfo',
      name: 'siteInfo',
      component: SiteInfoView
    },
    {
      path: '/txManager',
      name: 'txManager',
      component: TxManagerView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { doesNotRequireAuth: true }
    },
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  if (to.meta.doesNotRequireAuth || isAuthenticated) {
    next();
  } else {
    next('/login');
  }
});

export default router
