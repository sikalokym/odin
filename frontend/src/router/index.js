import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/Home.vue';
import Database from '@/components/Database.vue';
import Documents from '@/components/Documents.vue';
import Reports from '@/components/Reports.vue';
import { getRoles, ensureAuthenticated } from '@/authService';

/*
Routes
*/
const routes = [
	{
		path: '/',
		name: 'Home',
		component: Home,
		meta : {
			requiresRole: 'Reader',
		},
	},
	{
		path: '/database',
		name: 'Database',
		component: Database,
		meta: {
			requiresRole: 'Modifier',
		},
	},
	{
		path: '/documents',
		name: 'Documents',
		component: Documents,
		meta: {
			requiresRole: 'Reader',
		},
	},
	{
		path: '/reports',
		name: 'Reports',
		component: Reports,
		meta: {
			requiresRole: 'Modifier',
		},
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

// Global navigation guard for role-based access control
router.beforeEach(async (to, from, next) => {
	try {
	  await ensureAuthenticated();
	  if (to.matched.some(record => record.meta.requiresRole)) {
		const roles = await getRoles();
		const requiredRole = to.meta.requiresRole;
		if (roles.includes(requiredRole)) {
		  next();
		} else {
		  next('/');
		}
	  } else {
		next();
	  }
	} catch (error) {
	  console.error('Authentication error:', error);
	  next('/');
	}
  });
  
  export default router;