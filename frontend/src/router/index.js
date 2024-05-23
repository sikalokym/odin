import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/Home.vue';
import Database from '@/components/Database.vue';
import Documents from '@/components/Documents.vue';
import Reports from '@/components/Reports.vue';
import { getRoles } from '@/authService';

/*
Routes
*/
const routes = [
	{ path: '/', name: 'Home', component: Home },
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
		component: Documents
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
});

export default router;
