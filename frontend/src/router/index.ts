import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import LoginPage from '@/views/auth/LoginPage.vue'
import SignUpPage from '@/views/auth/SignUpPage.vue'
import AdminLoginPage from '@/views/auth/AdminLoginPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/court',
      name: 'courts',
      component: () => import('@/views/CourtsPage.vue'),
    },
    {
      path: '/court/:id',
      name: 'court-detail',
      component: () => import('@/views/CourtDetailPage.vue'),
    },
    {
      path: '/booking/:id',
      name: 'booking',
      component: () => import('@/views/BookingPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpPage,
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLoginPage,
    },
    {
      path: '/user/home',
      name: 'user-home',
      component: () => import('@/views/user/UserHomePage.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/user/streaks',
      component: () => import('@/layouts/UserStreaksLayout.vue'),
      meta: { requiresAuth: true, role: 'user' },
      redirect: '/user/streaks/friends',
      children: [
        {
          path: 'friends',
          name: 'user-streaks-friends',
          component: () => import('@/views/user/UserStreaksFriendsPage.vue'),
        },
        {
          path: 'overview',
          name: 'user-streaks-overview',
          component: () => import('@/views/user/UserStreaksOverviewPage.vue'),
        },
      ],
    },
    {
      path: '/owner/home',
      name: 'owner-home',
      component: () => import('@/views/owner/OwnerHomePage.vue'),
      meta: { requiresAuth: true, role: 'owner' },
    },
    // Owner Management routes
    {
      path: '/owner/management',
      component: () => import('@/layouts/OwnerManagementLayout.vue'),
      meta: { requiresAuth: true, role: 'owner' },
      children: [
        {
          path: 'revenue',
          name: 'owner-revenue',
          component: () => import('@/views/owner/OwnerRevenueStatisticsPage.vue'),
        },
        {
          path: 'courts',
          name: 'owner-courts',
          component: () => import('@/views/owner/OwnerCourtUploadPage.vue'),
        },
        {
          path: 'court-list',
          name: 'owner-court-list',
          component: () => import('@/views/owner/OwnerCourtListPage.vue'),
        },
        {
          path: 'bookings',
          name: 'owner-bookings',
          component: () => import('@/views/owner/OwnerBookingSchedulePage.vue'),
        },
      ],
    },
    {
      path: '/enterprise/home',
      name: 'enterprise-home',
      component: () => import('@/views/enterprise/EnterpriseHomePage.vue'),
      meta: { requiresAuth: true, role: 'enterprise' },
    },
    // Enterprise Advertisement Management routes
    {
      path: '/enterprise/advertisements',
      component: () => import('@/layouts/EnterpriseAdvertisementLayout.vue'),
      meta: { requiresAuth: true, role: 'enterprise' },
      redirect: '/enterprise/advertisements/list',
      children: [
        {
          path: 'upload',
          name: 'enterprise-advertisement-upload',
          component: () => import('@/views/enterprise/EnterpriseAdvertisementUploadPage.vue'),
        },
        {
          path: 'list',
          name: 'enterprise-advertisement-list',
          component: () => import('@/views/enterprise/EnterpriseAdvertisementListPage.vue'),
        },
      ],
    },
    // Admin routes
    {
      path: '/admin/profile',
      name: 'admin-profile',
      component: () => import('@/views/admin/AdminProfilePage.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/AdminUsersPage.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/courts',
      name: 'admin-courts',
      component: () => import('@/views/admin/AdminCourtPage.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/requests',
      name: 'admin-requests',
      component: () => import('@/views/admin/AdminRequestPage.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
  ],
})

// Simple navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')

  console.log('🔍 Router Guard:', {
    to: to.path,
    from: from.path,
    hasToken: !!token,
    hasUser: !!userStr,
  })

  // Redirect authenticated users from home page to their dashboard
  if (to.path === '/' && token && userStr) {
    try {
      const user = JSON.parse(userStr)
      console.log('🏠 Authenticated user accessing home, redirect to dashboard')
      // Redirect to appropriate dashboard based on role
      if (user.role === 'admin') {
        return next('/admin/profile')
      }
      return next(`/${user.role}/home`)
    } catch (e) {
      console.error('Error parsing user:', e)
    }
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!token || !userStr) {
      console.log('❌ Not authenticated, redirect to login')
      return next('/login')
    }

    // Check role
    try {
      const user = JSON.parse(userStr)
      if (to.meta.role && to.meta.role !== user.role) {
        console.log('❌ Wrong role, redirect to correct home')
        // Redirect admin to profile, others to their home
        if (user.role === 'admin') {
          return next('/admin/profile')
        }
        return next(`/${user.role}/home`)
      }
    } catch (e) {
      console.error('Error parsing user:', e)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return next('/login')
    }
  }

  // Allow signup with specific role parameter even if logged in (for partner registration)
  if (to.path === '/signup' && to.query.role && token && userStr) {
    console.log('🔓 Allowing signup access with role parameter')
    return next()
  }

  if ((to.path === '/login' || to.path === '/signup') && token && userStr) {
    try {
      const user = JSON.parse(userStr)
      console.log('✅ Already logged in, redirect to home')
      // Redirect admin to profile page, others to their home page
      if (user.role === 'admin') {
        return next('/admin/profile')
      }
      return next(`/${user.role}/home`)
    } catch (e) {
      console.error('Error parsing user:', e)
    }
  }

  // Redirect admin login page if already logged in as admin
  if (to.path === '/admin/login' && token && userStr) {
    try {
      const user = JSON.parse(userStr)
      if (user.role === 'admin') {
        console.log('✅ Admin already logged in, redirect to dashboard')
        return next('/admin/profile')
      }
    } catch (e) {
      console.error('Error parsing user:', e)
    }
  }

  next()
})

export default router
