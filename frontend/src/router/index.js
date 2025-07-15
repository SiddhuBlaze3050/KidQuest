import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import ChildDashboard from '../views/ChildDashboard.vue'
import { userUtils } from '@/services/api'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import ParentDashboard from '../views/ParentDashboard.vue'
import PyschometricAssessment from '../views/PyschometricAssessment.vue'
import GoodTouchBadTouchModule from '../views/GoodTouchBadTouchModule.vue'
import ScienceExplorerModule from '../views/ScienceExplorerModule.vue'
import WordWizardModule from '../views/WordWizardModule.vue'
import MathMagicModule from '../views/MathMagicModule.vue'
import SafetyMeasuresModule from '../views/SafetyMeasuresModule.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user && user.role === 'admin') {
          next()
        } else {
          next('/')
        }
      },
    },
    {
      path: '/child-dashboard',
      name: 'child-dashboard',
      component: ChildDashboard,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user && user.role === 'child') {
          next()
        } else {
          // For demo purposes, allow any logged-in user to access child dashboard
          if (user) {
            next()
          } else {
            next('/')
          }
        }
      },
    },
    {
      path: '/parent-dashboard',
      name: 'parent-dashboard',
      component: ParentDashboard,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user && user.role === 'parent') {
          next()
        } else {
          // For demo purposes, allow any logged-in user to access parent dashboard
          if (user) {
            next()
          } else {
            next('/')
          }
        }
      },
    },
    {
      path: '/teacher-dashboard',
      name: 'teacher-dashboard',
      component: TeacherDashboard,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user && user.role === 'teacher') {
          next()
        } else {
          // For demo purposes, allow any logged-in user to access teacher dashboard
          if (user) {
            next()
          } else {
            next('/')
          }
        }
      },
    },
    {
      path: '/psychometric-assessment',
      name: 'psychometric-assessment',
      component: PyschometricAssessment,
    },
    {
      path: '/good-touch-bad-touch',
      name: 'good-touch-bad-touch',
      component: GoodTouchBadTouchModule,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user) {
          next()
        } else {
          next('/')
        }
      },
    },
    {
      path: '/science-explorer',
      name: 'science-explorer',
      component: ScienceExplorerModule,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user) {
          next()
        } else {
          next('/')
        }
      },
    },
    {
      path: '/word-wizard',
      name: 'word-wizard',
      component: WordWizardModule,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user) {
          next()
        } else {
          next('/')
        }
      },
    },
    {
      path: '/math-magic',
      name: 'math-magic',
      component: MathMagicModule,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user) {
          next()
        } else {
          next('/')
        }
      },
    },
    {
      path: '/safety-measures',
      name: 'safety-measures',
      component: SafetyMeasuresModule,
      beforeEnter: (to, from, next) => {
        const user = userUtils.getCurrentUser()
        if (user) {
          next()
        } else {
          next('/')
        }
      },
    },
    // Redirect any unknown routes to home
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

export default router
