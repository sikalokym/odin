import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'

import router from './router'
import { initializeMsal } from './authConfig';


let app = createApp(App)
const pinia = createPinia()

initializeMsal().then(() => {
    app.use(router);
    app.use(pinia);
    app.mount('#app');
  });
