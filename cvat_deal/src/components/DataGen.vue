<template>
    <div class="card">
        <div class="bg">
            <div class="jobs_text">
                <n-popover trigger="hover">
                    <template #trigger>
                        <n-button type="info" dashed class="title_btn">
                            待生成路径:
                        </n-button>
                    </template>
                    <span>
                        <n-alert title="注意：" class="pop-note" type="warning" :bordered="false">
                            生成选择目录下需包含images、labels、classes.txt<br/>
                            images:图像文件夹<br/>
                            labels:标签文件夹<br/>
                            classes.txt:类别文件<br/>
                            警告：生成格式保存在本级目录下
                        </n-alert>
                    </span>
                </n-popover>
                <n-input
                        type="text"
                        spellcheck="false"
                        v-model:value="globalsetting_conf.will_gen_save_path"
                        class="input_value"
                        placeholder="选择目录"
                        @change="change_will_gen_save_path()"
                        clearable>
                </n-input>
            </div>
            <n-divider :vertical="true" class="divier_line"/>
            <div class="jobs_btn">
                <button class="btn" @click="select_dir('will_gen_save_path')">
                    文件夹选择
                </button>
                <!--<button class="button">文件夹选择</button>-->
            </div>

        </div>
        <!--<div class="blob"></div>-->
    </div>
    <n-divider/>
    <button class="button" @click="this.start_gen()">
        <span>开始生成</span>
        <svg height="16" width="16" xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 1024 1024">
            <path d="M523.81 117.87c-15.91 15.91-15.91 41.62 0 57.53l296.74 296.75H105.01c-22.46 0-40.69 18.23-40.69 40.68 0 22.46 18.23 40.69 40.69 40.69h715.55L523.81 850.26c-15.91 15.91-15.91 41.63 0 57.53 15.91 15.91 41.62 15.91 57.53 0L947.5 541.6c3.79-3.74 6.75-8.26 8.83-13.27a40.04 40.04 0 0 0 3.13-15.5c0-5.29-1.06-10.58-3.13-15.54-2.08-5.01-5.05-9.48-8.83-13.27L581.35 117.83c-15.92-15.87-41.63-15.87-57.54 0.04z" p-id="5896"></path>
        </svg>
    </button>
    <!-- 下载进度条-->
    <n-progress type="circle" class="cir_progress" :percentage="progress_val" />
</template>


<script>
    import {defineComponent} from "vue";
    import {set_conf, open_dir, start_gencvat, get_gencvat_progress} from "@/api/request";
    import {mapMutations, mapState} from "vuex";
    export default defineComponent({
        name: 'DataGenComponent',
        computed: {
            ...mapState(['globalsetting_conf']) // 从 Vuex 获取全局状态
        },
        data() {
            return {
                jobs: "",
                jobList: [],
                progress_val: 0,
            };
        },
        mounted() {

        },
        methods: {
            ...mapMutations(['setGlobalSetting_conf']), // 使用 mutation 更新全局状态
            start_gen() {
                start_gencvat(this.globalsetting_conf.will_gen_save_path).then((res)=>{
                    console.log("res", res)
                })
                this.progress_val = 0;
                // 设置一个100毫秒后执行的定时器
                var intervalId = setInterval(() => {  // 使用箭头函数确保 `this` 指向正确
                    get_gencvat_progress().then((res)=>{
                        this.progress_val = res.data.gen_status["progress"]
                    })
                    // this.progress_val += 10;  // 直接修改 progress_val
                    if (this.progress_val >= 100) {
                        clearInterval(intervalId);
                    }
                }, 100);
            },
            select_dir(type_name) {
                open_dir(type_name)
                    .then((response) => {
                        if (response.data.code === 201) {
                            this.setGlobalSetting_conf({
                                ...this.globalsetting_conf,
                                [type_name]: response.data.folder_path
                            });
                            set_conf(
                                this.globalsetting_conf.cookie,
                                this.globalsetting_conf.class_path,
                                this.globalsetting_conf.down_save_path,
                                this.globalsetting_conf.gen_save_path,
                                this.globalsetting_conf.will_change_path,
                                this.globalsetting_conf.will_gen_save_path
                            ).catch((error) => {
                                console.error("错误请求", error); // 错误处理
                            });
                        }
                    })
                    .catch((error) => {
                        console.error("错误请求", error); // 错误处理
                    });
            },
            change_will_gen_save_path(){
                set_conf(
                                this.globalsetting_conf.cookie,
                                this.globalsetting_conf.class_path,
                                this.globalsetting_conf.down_save_path,
                                this.globalsetting_conf.gen_save_path,
                                this.globalsetting_conf.will_change_path,
                                this.globalsetting_conf.will_gen_save_path
                            ).catch((error) => {
                                console.error("错误请求", error); // 错误处理
                            });
            }
        }
    });

</script>

<style scoped>
    /* From Uiverse.io by dylanharriscameron */
    .card {
        position: relative;
        width: 80%;
        height: 100px;
        border-radius: 14px;
        z-index: 1111;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff;;
        margin-left: 10%;
    }

    .bg {
        position: absolute;
        top: 5px;
        left: 5px;
        width: 100%;
        height: 190px;
        z-index: 2;
        background: rgba(255, 255, 255, .95);
        backdrop-filter: blur(24px);
        border-radius: 10px;
        overflow: hidden;
        outline: 2px solid white;
    }

    .blob {
        position: absolute;
        z-index: 1;
        top: 50%;
        left: 50%;
        width: 40%;
        height: 150px;
        border-radius: 50%;
        background-color: #005193;
        opacity: 1;
        filter: blur(12px);
        animation: blob-bounce 5s infinite ease;
    }

    @keyframes blob-bounce {
        0% {
            transform: translate(-100%, -100%) translate3d(0, 0, 0);
        }

        25% {
            transform: translate(-100%, -100%) translate3d(100%, 0, 0);
        }

        50% {
            transform: translate(-100%, -100%) translate3d(100%, 100%, 0);
        }

        75% {
            transform: translate(-100%, -100%) translate3d(0, 100%, 0);
        }

        100% {
            transform: translate(-100%, -100%) translate3d(0, 0, 0);
        }
    }

    .pop-note {
        background-color: #ffffff;
    }

    .jobs_text {
        width: 65%;
        height: 80px;
        margin-left: 1%;
        float: left;
        display: flex;
        align-items: center;
    }

    .title_btn {
        margin-top: 1.8%;
        color: #005193;
        float: left;
        height: 50%;
        margin-left: 6%;
    }

    .divier_line {
        height: 100px;
    }

    .jobs_btn {
        height: 50%;
        display: flex;
        align-items: center;
        width: 20%;
        float: right;
    }

    .input_value {
        height: 40%;
        width: 80%;
        margin-top: 2%;
        margin-left: 2%;
        text-align: left;
    }

    /* From Uiverse.io by CYBWEBALI */
    .btn {
        display: grid;
        place-items: center;
        background: #e3edf7;
        padding: 1.4em;
        border-radius: 10px;
        box-shadow: 6px 6px 10px -1px rgba(0, 0, 0, 0.15),
        -6px -6px 10px -1px rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(0, 0, 0, 0);
        cursor: pointer;
        transition: transform 0.5s;
        color: #005193;
        font-weight: bolder;
    }

    .btn:hover {
        box-shadow: inset 4px 4px 6px -1px rgba(0, 0, 0, 0.2),
        inset -4px -4px 6px -1px rgba(255, 255, 255, 0.7),
        -0.5px -0.5px 0px rgba(255, 255, 255, 1),
        0.5px 0.5px 0px rgba(0, 0, 0, 0.15),
        0px 12px 10px -10px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.1);
        transform: translateY(0.5em);
    }

    .btn svg {
        transition: transform 0.5s;
    }

    .btn:hover svg {
        transform: scale(0.9);
        fill: #333333;
    }


    .table-content {
        width: 80%;
        margin-top: 2%;
        margin-left: 10%;
        height: 600px;
        overflow-y: auto; /* 添加滚动 */
        margin-bottom: 20px;
    }

    .down_progress {
        width: 60%;
    }

    /* From Uiverse.io by Jedi-hongbin */
    .button {
        display: flex;
        height: 3em;
        width: 10%;
        align-items: center;
        justify-content: center;
        background-color: #eeeeee4b;
        border-radius: 3px;
        letter-spacing: 1px;
        transition: all 0.2s linear;
        cursor: pointer;
        background: #fff;
        border: none;
        font-weight: bolder;
        margin-left: 45%;
    }

    .button > svg {
        margin-right: 5px;
        margin-left: 5px;
        font-size: 20px;
        transition: all 0.4s ease-in;
    }

    .button:hover > svg {
        font-size: 1.2em;
        transform: translateX(10px);
    }

    .button:hover {
        box-shadow: 9px 9px 33px #d1d1d1, -9px -9px 33px #ffffff;
        transform: translateY(-2px);
    }
    .cir_progress{
        width: 20%;
        margin-top: 40px;
    }
</style>
