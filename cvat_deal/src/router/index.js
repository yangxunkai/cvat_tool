import { createRouter, createWebHashHistory } from 'vue-router';
import IndexComponent from '@/components/Index.vue';
import DatadownComponent from "@/components/DataDown.vue";
import DataChangeComponent from "@/components/DataChange";
import DataGenComponent from "@/components/DataGen";

const routes = [
    {
        path: '/',
        name: 'Index',
        component: IndexComponent,
    },
    {
        path: '/datadown',
        name: 'Datadown',
        component: DatadownComponent,
    },
    {
        path: '/datachange',
        name: 'Datachange',
        component: DataChangeComponent,
    },
    {
        path: '/datagen',
        name: 'Datagen',
        component: DataGenComponent,
    }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

// 添加全局前置守卫
router.beforeEach((to, from, next) => {
    // 如果路径是空的或者是根路径，并且目标路由不是 Index 才进行重定向
    if ((to.path === '' || to.path === '/') && to.name !== 'Index') {
        next({ name: 'Index' });  // 跳转到 Index
    } else {
        next();  // 继续导航
    }
});


export default router;
