import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import ChildDashboard from '../views/ChildDashboard.vue'
import ChildForm from '../views/ChildForm.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import TeacherAnalytics from '../views/TeacherAnalytics.vue'
import ParentDashboard from '../views/ParentDashboard.vue'
import PyschometricAssessment from '../views/PyschometricAssessment.vue'
import GoodTouchBadTouchModule from '../views/GoodTouchBadTouchModule.vue'
import ScienceExplorerModule from '../views/ScienceExplorerModule.vue'
import WordWizardModule from '../views/WordWizardModule.vue'
import MathMagicModule from '../views/MathMagicModule.vue'
import SafetyMeasuresModule from '../views/SafetyMeasuresModule.vue'
import authService from '@/services/authService'

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
        if (authService.isAuthenticated() && authService.hasRole('admin')) {
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
        console.log('🔍 Child dashboard route guard triggered')
        console.log('� Route details - to:', to.path, 'from:', from.path)
        console.log('�📋 Authentication status:', authService.isAuthenticated())
        console.log('👤 Current user:', authService.getCurrentUser())
        console.log('🎭 Has child role:', authService.hasRole('child'))
        console.log('🔧 Token exists:', !!authService.getToken())
        console.log('🔧 User data exists:', !!authService.getUser())
        
        const isAuth = authService.isAuthenticated()
        const hasChildRole = authService.hasRole('child')
        
        console.log('🔍 Final checks - isAuth:', isAuth, 'hasChildRole:', hasChildRole)
        
        if (isAuth && hasChildRole) {
          console.log('✅ Access granted: Child authenticated')
          console.log('🎯 Proceeding to child dashboard...')
          next()
        } else {
          console.log('❌ Access denied: User is not a child or not authenticated')
          console.log('🔍 Auth state:', { isAuth, hasChildRole })
          console.log('🔍 Redirecting to home page')
          next('/')
        }
      },
    },
    {
      path: '/child-form',
      name: 'child-form',
      component: ChildForm,
    },
    {
      path: '/parent-dashboard',
      name: 'parent-dashboard',
      component: ParentDashboard,
      beforeEnter: (to, from, next) => {
        if (authService.isAuthenticated() && authService.hasRole('parent')) {
          next()
        } else {
          console.log('❌ Access denied: User is not a parent or not authenticated')
          next('/')
        }
      },
    },
    {
      path: '/teacher-dashboard',
      name: 'teacher-dashboard',
      component: TeacherDashboard,
      beforeEnter: (to, from, next) => {
        console.log('🔍 Teacher dashboard route guard triggered')
        console.log('📋 Authentication status:', authService.isAuthenticated())
        console.log('👤 Current user:', authService.getCurrentUser())
        console.log('🎭 Has teacher role:', authService.hasRole('teacher'))
        
        if (authService.isAuthenticated() && authService.hasRole('teacher')) {
          console.log('✅ Access granted: Teacher authenticated')
          next()
        } else {
          console.log('❌ Access denied: User is not a teacher or not authenticated')
          console.log('🔍 Redirecting to home page')
          next('/')
        }
      },
    },
    {
      path: '/teacher-analytics',
      name: 'teacher-analytics',
      component: TeacherAnalytics,
      beforeEnter: (to, from, next) => {
        console.log('🔍 Teacher analytics route guard triggered')
        console.log('📋 Authentication status:', authService.isAuthenticated())
        console.log('👤 Current user:', authService.getCurrentUser())
        console.log('🎭 Has teacher role:', authService.hasRole('teacher'))
        
        if (authService.isAuthenticated() && authService.hasRole('teacher')) {
          console.log('✅ Access granted: Teacher authenticated for analytics')
          next()
        } else {
          console.log('❌ Access denied: User is not a teacher or not authenticated')
          console.log('🔍 Redirecting to home page')
          next('/')
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
        if (authService.isAuthenticated()) {
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
        if (authService.isAuthenticated()) {
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
        if (authService.isAuthenticated()) {
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
        if (authService.isAuthenticated()) {
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
        if (authService.isAuthenticated()) {
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
