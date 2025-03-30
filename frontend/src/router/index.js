import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/Home.vue';
import Database from '@/components/Database.vue';
import Documents from '@/components/Documents.vue';
import Reports from '@/components/Reports.vue';
import { ensureAuthenticated } from '@/authService';
import { useAuthStore } from '../stores/auth';
import { useEntitiesStore } from '../stores/entities.js'

/*
Routes
*/
const routes = [
	{
		path: '/',
		name: 'Home',
		component: Home,
		meta: {
			requiresRole: ['reader', 'modifier']
		},
	},
	{
		path: '/database',
		name: 'Database',
		component: Database,
		meta: {
			requiresRole: ['modifier'],
		},
	},
	{
		path: '/documents',
		name: 'Documents',
		component: Documents,
		meta: {
			requiresRole: ['reader', 'modifier']
		},
	},
	{
		path: '/reports',
		name: 'Reports',
		component: Reports,
		meta: {
			requiresRole: ['modifier'],
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
		let roles = useAuthStore().getCountriesRoles();
		let entStore = useEntitiesStore();
		let curr_country = entStore.country;
		if (!curr_country) {
			await new Promise(resolve => setTimeout(resolve, 1000));
			next('/');
			return;
		}
		if (to.matched.some(record => record.meta.requiresRole)) {
			const requiredRole = to.meta.requiresRole;
			// filter roles with requiredRole
			// roles = roles.filter(role => role.country.toLowerCase() === curr_country.CountryName.toLowerCase());
			roles = roles.filter(role => role.split(".")[0] === curr_country.Code);
			roles = roles.map(role => role.split(".")[1]);
			
			if (requiredRole.some(role => roles.includes(role))) {
				next();
				console.log('User has the required role:', requiredRole);
			} else {
				console.log('User does not have the required role:', requiredRole);
				next('/');
			}
		} else {
			console.log('No required role for this route');
			next('/');
		}
	} catch (error) {
		console.error('Authentication error:', error);
		next('/');
	}
});

export default router;