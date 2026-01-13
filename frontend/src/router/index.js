import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ItemsList from '../views/ItemsList.vue'
import AddItem from '../views/AddItem.vue'
import ItemDetail from '../views/ItemDetail.vue'
import Locations from '../views/Locations.vue'
import Categories from '../views/Categories.vue'
import Settings from '../views/Settings.vue'
import Setup from '../views/Setup.vue'

const routes = [
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
    component: Setup
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
