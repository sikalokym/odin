import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'

import 'notyf/notyf.min.css';

import router from './router'

// import { Notyf } from 'notyf';
// const notyf = new Notyf({
// 	position: { x: 'center', y: 'top' }
// });


let myApp = createApp(App)
const pinia = createPinia()

myApp.use(router)
myApp.use(pinia)
// myApp.use(notyf)

myApp.mount('#app')
