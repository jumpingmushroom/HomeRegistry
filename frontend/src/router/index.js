import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ItemsList from '../views/ItemsList.vue'
import AddItem from '../views/AddItem.vue'
import ItemDetail from '../views/ItemDetail.vue'
import Locations from '../views/Locations.vue'
import Categories from '../views/Categories.vue'
import Settings from '../views/Settings.vue'
import Setup from '../views/Setup.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import PublicItemView from '../views/PublicItemView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { public: true }
  },
  {
    path: '/public/items/:id',
    name: 'PublicItemView',
    component: PublicItemView,
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/items',
    name: 'Items',
    component: ItemsList
  },
  {
    path: '/items/add',
    name: 'AddItem',
    component: AddItem
  },
  {
    path: '/items/:id',
    name: 'ItemDetail',
    component: ItemDetail
  },
  {
    path: '/locations',
    name: 'Locations',
    component: Locations
  },
  {
    path: '/categories',
    name: 'Categories',
    component: Categories
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/setup',
    name: 'Setup',
    component: Setup,
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
