import { createApp } from 'vue';
import App from './App.vue';
import naive from 'naive-ui';  // 引入 Naive UI
import router from './router'; // 引入路由
import store from './store'; // 引入 Vuex Store

const app = createApp(App);
app.use(naive);  // 使用 Naive UI
app.use(router);  // 使用 router
app.use(store);   // 使用 Vuex Store
app.mount('#app');