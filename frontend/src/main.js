import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'

// import { Notyf } from 'notyf';
import 'notyf/notyf.min.css';

import router from './router'

// const notyf = new Notyf({
// 	position: { x: 'center', y: 'top' }
// });
/*const pinia = createPinia()*/


let myApp = createApp(App)

myApp.use(createPinia())
/*myApp.use(pinia)*/
// myApp.use(notyf)
myApp.use(router)

myApp.mount('#app')
