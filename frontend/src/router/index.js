import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/components/Home.vue';
import Database from '@/components/Database.vue';
import Documents from '@/components/Documents.vue';
import Reports from '@/components/Reports.vue';

/*
Routes
*/
const routes = [
	{ path: '/', name: 'Home', component: Home },
	{ path: '/database', name: 'Database', component: Database },
	{ path: '/documents', name: 'Documents', component: Documents },
	{ path: '/reports', name: 'Reports', component: Reports },
]
const router = createRouter({
	history: createWebHistory(),
	routes
  })

export default router;
