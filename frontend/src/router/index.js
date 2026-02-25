import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/public/items/:id',
    name: 'PublicItemView',
    component: () => import('../views/PublicItemView.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('../views/ItemsList.vue')
  },
  {
    path: '/items/add',
    name: 'AddItem',
    component: () => import('../views/AddItem.vue')
  },
  {
    path: '/items/:id',
    name: 'ItemDetail',
    component: () => import('../views/ItemDetail.vue')
  },
  {
    path: '/locations',
    name: 'Locations',
    component: () => import('../views/Locations.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('../views/Setup.vue'),
    meta: { public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const isPublicRoute = to.meta.public === true

  // If it's a public route, allow access
  if (isPublicRoute) {
    // If user is logged in and trying to access login/register, redirect to dashboard
    if (token && (to.name === 'Login' || to.name === 'Register')) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
    return
  }

  // For protected routes, check if user is authenticated
  if (!token) {
    // Check if any users exist - if not, redirect to register
    try {
      const { useAuthStore } = await import('../stores/auth')
      const authStore = useAuthStore()
      const status = await authStore.checkAuthStatus()

      if (!status.has_users) {
        next({ name: 'Register' })
      } else {
        next({ name: 'Login' })
      }
    } catch (error) {
      next({ name: 'Login' })
    }
    return
  }

  // User has token, allow access
  next()
})

export default router
