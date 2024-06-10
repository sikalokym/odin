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
			requiresRole: ['readers', 'modifiers']
		},
	},
	{
		path: '/database',
		name: 'Database',
		component: Database,
		meta: {
			requiresRole: ['modifiers'],
		},
	},
	{
		path: '/documents',
		name: 'Documents',
		component: Documents,
		meta: {
			requiresRole: ['readers', 'modifiers']
		},
	},
	{
		path: '/reports',
		name: 'Reports',
		component: Reports,
		meta: {
			requiresRole: ['modifiers'],
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
			await entStore.fetchSupportedCountries(roles.map(role => role.country.toLowerCase()));
			curr_country = useEntitiesStore().country;
		}
		console.log('Current country:', curr_country);
		if (to.matched.some(record => record.meta.requiresRole)) {
			const requiredRole = to.meta.requiresRole;
			// filter roles with requiredRole
			roles = roles.filter(role => role.country.toLowerCase() === curr_country.CountryName.toLowerCase());
			roles = roles.map(role => role.role);
			
			if (requiredRole.some(role => roles.includes(role))) {
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