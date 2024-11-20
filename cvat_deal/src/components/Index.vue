<template>
    <div class="header-left" @click="refreshPage">
        <img src="../assets/logo.png" alt="Logo" class="logo"/>
    </div>
    <n-split :default-size="0.8" class="menu">
        <template #1>
            <n-menu
                    class="_menu"
                    v-model:value="activeKey"
                    mode="horizontal"
                    :options="menuOptions"
                    responsive
            />
        </template>
    </n-split>

    <div class="header_icon">
        <!--    这是删除图标-->
        <n-icon size="25" @click="open_delete()" class="delete">
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 20 20">
                <g fill="none">
                    <path d="M11.5 4a1.5 1.5 0 0 0-3 0h-1a2.5 2.5 0 0 1 5 0H17a.5.5 0 0 1 0 1h-.554L15.15 16.23A2 2 0 0 1 13.163 18H6.837a2 2 0 0 1-1.987-1.77L3.553 5H3a.5.5 0 0 1-.492-.41L2.5 4.5A.5.5 0 0 1 3 4h8.5zm3.938 1H4.561l1.282 11.115a1 1 0 0 0 .994.885h6.326a1 1 0 0 0 .993-.885L15.438 5zM8.5 7.5c.245 0 .45.155.492.359L9 7.938v6.125c0 .241-.224.437-.5.437c-.245 0-.45-.155-.492-.359L8 14.062V7.939c0-.242.224-.438.5-.438zm3 0c.245 0 .45.155.492.359l.008.079v6.125c0 .241-.224.437-.5.437c-.245 0-.45-.155-.492-.359L11 14.062V7.939c0-.242.224-.438.5-.438z"
                          fill="currentColor"></path>
                </g>
            </svg>
        </n-icon>
        <!--    这是设置图标-->
        <n-icon size="25" @click="open_setting()" class="setting">
            <SettingsOutline/>
        </n-icon>

    </div>
    <!--    弹出删除界面-->
    <n-modal v-model:show="delete_showModal" transform-origin="center">
        <n-card
                style="width: 800px"
                title="CVAT服务器压缩包缓存查询和清空"
                :bordered="false"
                size="huge"
                role="dialog"
                aria-modal="true"
        >
            <template #header-extra>
                <n-icon size="20" @click="delete_showModal = false" class="close_svg">
                    <CloseOutline/>
                </n-icon>
            </template>
            <div class="delete_left">
                <div class="input_itema">
                    <span class="title_texta">ip:</span>
                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.cvat_ip" placeholder="cvat部署服务器ip" class="text_value" clearable/>
                </div>
                <div class="input_itema">
                    <p class="title_texta">账号:</p>
                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.serve_username" placeholder="cvat部署服务器用户名" class="text_value" clearable/>
                </div>
                <div class="input_itema">
                    <p class="title_texta">密码:</p>
                    <n-input type="password" show-password-on="mousedown" spellcheck="false" v-model:value="globalsetting_conf.serve_password" placeholder="cvat部署服务器密码" class="text_value" clearable/>
                </div>
            </div>
            <n-divider vertical style="height: 200px"/>
            <div class="delete_right" v-if="this.jobDellists.length>0">
                <div v-for="job in jobDellists" :key="job.jobId" :v-if="jobDellists.length>0">
                    <n-space class="del_job_tag">
                        <n-tag type="success" size="small" round closable @close="delete_one(job.jobId)">
                            job{{job.jobId}}
                        </n-tag>
                    </n-space>
                </div>
            </div>
            <div class="delete_right1" v-else>
                <img src="../assets/null.png" alt="Logo" class="logo1"/>
            </div>
            <template #footer>
                <n-button type="success" style="margin-left: 15%" @click="conn_serve()">
                    <div v-if="this.connshow">
                        <n-spin size="small" stroke="#ffffff">
                        </n-spin>
                    </div>
                    <div v-else>
                         查询缓存
                    </div>

                </n-button>
                <n-button type="success" v-if="this.jobDellists.length>0" style="margin-left: 40%" @click="del_serve()">
                    <div v-if="this.delshow">
                        <n-spin size="small" stroke="#ffffff">
                        </n-spin>
                    </div>
                    <div v-else>
                         删除所有
                    </div>
                </n-button>
            </template>

            <n-modal
                    v-model:show="showSubmit"
                    :mask-closable="false"
                    preset="dialog"
                    title=""
                    :content="showSubmit_Text"
                    positive-text="ok"
            />
        </n-card>
    </n-modal>

    <!--    弹出设置界面-->
    <n-modal v-model:show="setting_showModal" transform-origin="center">
        <n-card
                style="width: 600px"
                title="参数设置"
                :bordered="false"
                size="huge"
                role="dialog"
                aria-modal="true"
        >
            <template #header-extra>
                <n-icon size="20" @click="setting_showModal = false" class="close_svg">
                    <CloseOutline/>
                </n-icon>
            </template>
            <div>
                <div class="input_item0">
                    <p class="title_text0">Cookie:</p>
                    <n-input type="textarea" spellcheck="false" v-model:value="globalsetting_conf.cookie" placeholder="用户cookie数据" class="text_value0" round clearable/>
                </div>
                <div class="input_item1">
                    <p class="title_text1">CVAT IP:</p>
                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.cvat_ip" placeholder="cvat标注平台ip" class="text_value0" round clearable/>
                </div>
                <div class="input_item">
                    <span class="title_text">类别路径:</span>
                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.class_path" placeholder="类别文件路径" class="text_value" clearable/>
                    <n-button strong secondary circle type="success" class="select_icon" @click="select_dir('class_path')">
                        <template #icon>
                            <n-icon>
                                <DuplicateOutline/>
                            </n-icon>
                        </template>
                    </n-button>
                </div>
                <div class="input_item">
                    <p class="title_text">同时下载个数:</p>
                    <n-input-number v-model:value="globalsetting_conf.downnum" clearable  class="text_value1" placeholder="同时下载的个数"  />
                </div>
                <div class="input_item">
                    <p class="title_text">下载保存路径:</p>
                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.down_save_path" placeholder="下载保存的路径" class="text_value" clearable/>
                    <n-button strong secondary circle type="success" class="select_icon" @click="select_dir('down_save_path')">
                        <template #icon>
                            <n-icon>
                                <SaveOutline/>
                            </n-icon>
                        </template>
                    </n-button>
                </div>
<!--                <div class="input_item">-->
<!--                    <p class="title_text">生成保存路径:</p>-->
<!--                    <n-input type="text" spellcheck="false" v-model:value="globalsetting_conf.gen_save_path" placeholder="生成cvat格式保存路径" class="text_value" clearable/>-->
<!--                    <n-button strong secondary circle type="success" class="select_icon" @click="select_dir('gen_save_path')">-->
<!--                        <template #icon>-->
<!--                            <n-icon>-->
<!--                                <FolderOpenOutline/>-->
<!--                            </n-icon>-->
<!--                        </template>-->
<!--                    </n-button>-->
<!--                </div>-->
            </div>
            <template #footer>
                <n-button type="success" style="margin-left: 42%" @click="save_conf()">
                    保存配置
                </n-button>
            </template>

            <n-modal
                    v-model:show="showSubmit"
                    :mask-closable="false"
                    preset="dialog"
                    title=""
                    :content="showSubmit_Text"
                    positive-text="ok"
            />
        </n-card>
    </n-modal>

    <n-divider class="divider"/>
    <div v-if="activeKey === 'data_down'">
        <DataDownComponent/>
    </div>
    <div v-else-if="activeKey === 'data_change'">
        <DataChangeComponent/>
    </div>
    <div v-else>
        <DataGenComponent/>
<!--        <TestComponent/>-->
    </div>
</template>

<script>
    import {h, ref} from "vue";
    import {NIcon} from "naive-ui";
    import {mapState, mapMutations} from 'vuex'; // 引入 Vuex 用来映射状态和方法
    import DataDownComponent from "@/components/DataDown.vue";
    import DataChangeComponent from "@/components/DataChange.vue";
    import DataGenComponent from "@/components/DataGen.vue";
    // import TestComponent from "@/components/Test";
    import {obtain_conf, set_conf, open_dir, conn_cvat_ssh, del_cvat_onejob, del_cvat_jobs} from "@/api/request";
    import {
        CaretDownCircleOutline as CaretDownCircleOutline,
        ArrowRedoCircleOutline as ArrowRedoCircleOutline,
        HeartCircleOutline as HeartCircleOutline,
        SettingsOutline as SettingsOutline,
        CloseOutline as CloseOutline,
        // FolderOpenOutline as FolderOpenOutline,
        DuplicateOutline as DuplicateOutline,
        SaveOutline as SaveOutline
    } from "@vicons/ionicons5";
    function renderIcon(icon) {
        return () => h(NIcon, null, {default: () => h(icon)});
    }

    const menuOptions = [
        {
            label: "数据下载",
            key: "data_down",
            icon: renderIcon(CaretDownCircleOutline),
        },
        {
            label: "数据转换",
            key: "data_change",
            icon: renderIcon(ArrowRedoCircleOutline),
        },
        {
            label: "数据生成",
            key: "data_gen",
            icon: renderIcon(HeartCircleOutline),
        },
    ];

    export default {
        name: "IndexComponent",
        components: {
            SettingsOutline,
            CloseOutline,
            // FolderOpenOutline,
            DuplicateOutline,
            SaveOutline,
            DataDownComponent, // 注册组件
            DataChangeComponent,
            DataGenComponent,
            // TestComponent,
        },
        computed: {
            ...mapState(['globalsetting_conf']) // 从 Vuex 获取全局状态
        },
        data() {
            return {
                hover: false,
                setting_showModal: false,
                delete_showModal: false,
                showSubmit: false,
                showSubmit_Text: "",
                jobDellists: [],  // 这是您提供的 jobDellists
                connshow:false,
                delshow:false
            }
        },
        mounted() {
            obtain_conf()
                    .then((response) => {
                        this.setGlobalSetting_conf(response.data); // 更新全局配置
                    })
                    .catch((error) => {
                        console.error("错误请求", error); // 错误处理
                    });
        },
        methods: {
            ...mapMutations(['setGlobalSetting_conf']), // 使用 mutation 更新全局状态
            //刷新页面
            refreshPage() {
                window.location.reload();
            },
            //打开设置
            open_setting() {
                this.setting_showModal = true;
            },
            //打开删除
            open_delete(){
                this.delete_showModal = true;
            },
            //保存参数
            save_conf() {
                set_conf(
                    this.globalsetting_conf.cookie,
                    this.globalsetting_conf.class_path,
                    this.globalsetting_conf.down_save_path,
                    this.globalsetting_conf.gen_save_path,
                    "",
                    "",
                    this.globalsetting_conf.cvat_ip,
                    "",
                    "",
                    this.globalsetting_conf.downnum
                ).then((response) => {
                    if (response.data.message.includes("成功")) {
                        this.showSubmit_Text = response.data.message;
                    } else {
                        this.showSubmit_Text = response.data.message;
                    }
                    this.showSubmit = true;
                }).catch((error) => {
                    console.error("错误请求", error); // 错误处理
                    this.showSubmit_Text = "请求错误, 保存失败!";
                });
            },
            //选择文件夹
            select_dir(type_name) {
                open_dir(type_name)
                    .then((response) => {
                        if (response.data.code === 201) {
                            this.setGlobalSetting_conf({
                                ...this.globalsetting_conf,
                                [type_name]: response.data.folder_path
                            });
                        }
                    })
                    .catch((error) => {
                        console.error("错误请求", error); // 错误处理
                    });
            },
            //连接服务器
            conn_serve(){
                this.connshow = true
                console.log("连接服务器", this.globalsetting_conf.serve_username, this.globalsetting_conf.serve_password)
                set_conf(
                    this.globalsetting_conf.cookie,
                    this.globalsetting_conf.class_path,
                    this.globalsetting_conf.down_save_path,
                    this.globalsetting_conf.gen_save_path,
                    "",
                    "",
                    this.globalsetting_conf.cvat_ip,
                    this.globalsetting_conf.serve_username,
                    this.globalsetting_conf.serve_password,
                    this.globalsetting_conf.downnum
                ).then((response) => {
                    if (response.data.message.includes("成功")) {
                        //进行cvat_ssh连接查询
                        conn_cvat_ssh().then((res)=>{
                            this.jobDellists = res.data.output
                            if (res.data.message.includes("成功")){
                                this.showSubmit_Text = res.data.message;
                            }
                            else{
                                this.showSubmit_Text = res.data.message;
                            }
                            this.showSubmit = true;
                            this.connshow = false
                        })
                        this.showSubmit_Text = response.data.message;
                    } else {
                        this.showSubmit_Text = response.data.message;
                    }
                    // this.showSubmit = true;
                }).catch((error) => {
                    console.error("错误请求", error); // 错误处理
                    this.showSubmit_Text = "请求错误, 保存失败!";
                    this.showSubmit = true;
                });
            },

            del_serve(){
                this.delshow = true
                console.log("删除服务器id")
                del_cvat_jobs().then((res)=>{
                    console.log(res.data)
                    if(res.data.message.includes("成功")){
                        this.delshow = false
                        this.jobDellists=[]
                    }
                })

            },
            //删除一个job
            delete_one(id){
                console.log("delete_one", id)
                console.log("this.jobDellists", this.jobDellists)
                const job = this.jobDellists.find(item => item.jobId === id);
                del_cvat_onejob(job.jobName).then((res)=>{
                    console.log(res.data)
                    if(res.data.message.includes("成功")){
                        this.jobDellists = this.jobDellists.filter(item => item.jobId !== id);
                    }

                })
            }


        },
        setup() {
            const activeKey = ref('data_down');
            return {
                activeKey,
                menuOptions,
            };
        }
    }
</script>

<style scoped>
    .menu {
        display: flex;
        width: 60%;
        margin-left: 5%;
        height: 60px;
        align-items: center;
        float: left;
    }

    .header-left {
        display: flex;
        align-items: center;
        float: left;
    }

    .logo {
        width: 160px;
        height: 60px;
        margin-left: 30%;
    }
    .logo1 {
        width: 200px;
        height: 200px;
        margin-left: 20%;
    }

    .close_svg:hover {
        color: green;
    }

    .input_item0{
        height: 100px;
        display: flex;
        align-items: center;
    }
    .input_item1{
        height: 60px;
        display: flex;
        align-items: center;
    }

    .input_item {
        height: 60px;
        display: flex;
        align-items: center;
        margin-top: 1%;
    }
    .input_itema {
        height: 60px;
        display: flex;
        align-items: center;
        margin-top: 1%;
    }

    .title_text0, .title_text, .title_text1{
        float: left;
        width: 100px;
        text-align: left;
    }
    .title_texta{
        float: left;
        width: 40px;
    }

    .text_value0, .text_value, .text_value0{
        width: 70%;
        margin-left: 3%;
    }
    .text_value1{
        width: 40%;
        margin-left: 3%;
    }

    .select_icon {
        margin-left: 3%;
    }
    .header_icon{
        width: 100px;
        height: 60px;
        float: right;
        margin-right: 6%;
    }
    .setting {
        height: 60px;
        align-content: center;
    }
    .setting:hover {
        color: green;
    }
    .delete {
        height: 60px;
        align-content: center;
        float: left;
        margin-left: 10%}
    .delete:hover {
        color: green;
    }
    .divider {
        margin-top: 0;
    }
    .delete_left{
        width: 46%;
        float: left;
        height: 200px;
    }
    .delete_right{
        width: 46%;
        float: right;
        height: 200px;
        overflow-y: scroll; /* 启用纵向滚动 */
    }
    .delete_right1{
        width: 46%;
        height: 200px;
        float: right;
    }
    .del_job_tag{
        float: left;
        margin-left: 2%;
        margin-top: 5px;
    }
</style>
