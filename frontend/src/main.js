import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'

import router from './router'
import { initializeMsal } from './authConfig';
import { ensureAuthenticated } from './authService';

// Author: Hassan Wahba

const pinia = createPinia()

initializeMsal().then(async () => {
  let app = createApp(App)
  app.use(pinia);
  app.use(router);
  await ensureAuthenticated()
  app.mount('#app');
});
