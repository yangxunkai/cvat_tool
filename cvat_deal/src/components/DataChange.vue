<template>
    <div class="card">
        <div class="bg">

            <div class="jobs_text">
                <n-popover trigger="hover">
                    <template #trigger>
                        <n-button type="info" dashed class="title_btn">
                            待转换路径:
                        </n-button>
                    </template>
                    <span>
                        <n-alert title="注意：" class="pop-note" type="warning" :bordered="false">
                            将CVAT平台转换的标签转为yolo分割以及目标检测标签<br/>
                            转换完后压缩包统一解压到一个目录文件夹下，选择该目录文件夹<br/>
                            例如：<br/>
                            -cvat<br/>
                                &nbsp;&nbsp;&nbsp;&nbsp;--job_001_dataset_2024_09_27_06_16_07_cvat for images 1.1<br/>
                                &nbsp;&nbsp;&nbsp;&nbsp;--job_002_dataset_2024_09_27_06_17_07_cvat for images 1.1
                        </n-alert>
                    </span>
                </n-popover>
                <n-input
                        spellcheck="false"
                        type="text"
                        v-model:value="globalsetting_conf.will_change_path"
                        class="input_value"
                        placeholder="选择目录"
                        @change="change_will_change_path()"
                        clearable>
                </n-input>
            </div>
            <n-divider :vertical="true" class="divier_line"/>
            <div class="jobs_btn">
                <button class="button" @click="select_dir('will_change_path')">文件夹选择</button>
            </div>

        </div>
        <!--        <div class="blob"></div>-->
    </div>
    <n-divider/>
    <n-button strong round :type="isConverting ? 'error' : 'success'" @click="change_jobs()">
        {{ isConverting ? '暂停' : '转换全部' }}
    </n-button>
    <!--    解析转换表格-->
    <div class="table-content">
        <n-space vertical>
            <n-table virtual-scroll type="selection" striped>

                <thead>
                <tr>
                    <th>ID:</th>
                    <th>状态:</th>
                    <th>转换进度:</th>
                    <th style="text-align: center">操作</th>
                </tr>
                </thead>
                <tbody>
                <tr :v-if="jobList.length>0" v-for="job in jobList" :key="job.id">
                    <td>{{ job.id }}</td>
                    <td>
                        <n-tag :bordered="false"
                               :type="job.status === '转换完成' ? 'success':job.status === '转换中' ? 'info' : job.status === '生成中' ? 'warning' : 'error'">
                            {{ job.status }}
                        </n-tag>
                    </td>
                    <td style="width: 50%;text-align: left">
                        <n-progress
                                type="line"
                                :percentage=job.progress
                                indicator-placement="inside"
                                class="down_progress"
                                v-if="job.progress !== 0"
                                :color="job.progress === 100?themeVars.successColor:themeVars.infoColor"
                                :rail-color="changeColor(job.progress === 100?themeVars.successColor:themeVars.infoColor, { alpha: 0.2 })"
                        />
                        <div v-if="job.progress === 0" style="align-items: center">
                            <template v-if="job.status === '打包中'">
                                <n-spin :show="spin_show" size="small">
                                    <template #icon>
                                        <n-icon color="#F0A020">
                                            <SyncCircleOutline/>
                                        </n-icon>
                                    </template>
                                </n-spin>
                            </template>
                            <div v-else class="load_style">
                                -
                            </div>
                        </div>
                    </td>
                    <td style="width: 15%;text-align: center">
                        <n-button type="success" class="down_btn" @click="change_job(job.jobdir, job.id)">
                            <template v-if="job.down_loading">
                                <n-spin size="small" stroke="#ffffff">
                                </n-spin>
                            </template>
                            <div v-else class="load_style">
                                <div style="align-items: center; height: 100%;margin-top: 20%">
                                    转换
                                </div>
                            </div>
                        </n-button>
                    </td>
                </tr>
                </tbody>
            </n-table>
        </n-space>
    </div>
</template>


<script>
    import {defineComponent} from "vue";
    import {changeColor} from 'seemly'
    import {set_conf, open_dir, analysis_changedir, datatype_change, get_changeprogress} from "@/api/request";
    import {mapMutations, mapState} from "vuex";
    import {useThemeVars} from "naive-ui";

    export default defineComponent({
        name: 'DataChangeComponent',
        computed: {
            ...mapState(['globalsetting_conf']) // 从 Vuex 获取全局状态
        },
        data() {
            return {
                jobs: "",
                jobList: [],
                subfoldersList: [],
                themeVars: useThemeVars(),
                changeColor,
                show: false,
                isConverting:false
            };
        },
        mounted() {
            this.dirs_analysis(this.globalsetting_conf.will_change_path)
        },
        methods: {
            ...mapMutations(['setGlobalSetting_conf']), // 使用 mutation 更新全局状态
            dirs_analysis(file_dir) {
                this.jobList = []
                analysis_changedir(file_dir).then((res) => {
                    console.log("res", res.data)
                    if (res.data.subfolders) {
                        res.data.subfolders.map((item) => {
                            console.log(item.includes("job"))
                            if (item.includes("job") && item.includes("dataset")) {
                                this.jobList.push({
                                    id: item.split('job_')[1].split('_dataset')[0],
                                    jobdir: item,
                                    status: "待操作",
                                    progress: 0
                                })
                            }

                        })
                    }
                })
                this.jobList.sort((a, b) => a.id - b.id);
            },
            select_dir(type_name) {
                open_dir(type_name)
                    .then((response) => {
                        if (response.data.code === 201) {
                            this.setGlobalSetting_conf({
                                ...this.globalsetting_conf,
                                [type_name]: response.data.folder_path
                            });
                            this.dirs_analysis(response.data.folder_path)
                            set_conf(
                                this.globalsetting_conf.cookie,
                                this.globalsetting_conf.class_path,
                                this.globalsetting_conf.down_save_path,
                                this.globalsetting_conf.gen_save_path,
                                "",
                                this.globalsetting_conf.will_change_path
                            ).catch((error) => {
                                console.error("错误请求", error); // 错误处理
                            });
                        }
                    })
                    .catch((error) => {
                        console.error("错误请求", error); // 错误处理
                    });
            },
            change_will_change_path() {
                set_conf(
                    this.globalsetting_conf.cookie,
                    this.globalsetting_conf.class_path,
                    this.globalsetting_conf.down_save_path,
                    this.globalsetting_conf.gen_save_path,
                    "",
                    this.globalsetting_conf.will_change_path
                ).catch((error) => {
                    console.error("错误请求", error); // 错误处理
                });
            },
            get_oneprogress(task_id) {
                get_changeprogress(task_id).then((res) => {
                    console.log("res", res)
                })
            },
            change_job(task_dir, task_id) {
                //定时器获取任务进度
                const intervalId = setInterval(() => {
                    // 获取任务进度
                    get_changeprogress(task_id).then((progressInfo) => {

                        if (progressInfo.data.message.includes("完成")) {
                            // 如果进度达到100，清除定时器
                            console.log(`Task ${task_id} is complete!`);
                            progressInfo.data.task = {
                                "id": task_id,
                                "progress": 100,
                                "status": "转换完成"
                            }
                            clearInterval(intervalId);  // 销毁定时器
                        }
                        let _jobList = this.jobList
                        _jobList.map((it) => {
                            let task_id = 0
                            if (progressInfo.data.task["id"] !== undefined) {
                                task_id = parseInt(progressInfo.data.task["id"])
                            }
                            if (parseInt(it["id"]) === task_id) {
                                it['progress'] = progressInfo.data.task["progress"]
                                it['status'] = progressInfo.data.task["status"]
                            }
                            console.log("task_id", task_id)
                            if (progressInfo.data.message.includes("完成") && it["id"] === task_id) {
                                it['progress'] = 100
                                it['status'] = "已完成"
                            }
                        })
                        this.jobList = _jobList
                    }).catch(error => {
                        console.error("Error getting progress:", error);
                        clearInterval(intervalId);  // 销毁定时器，防止死循环
                    });
                }, 300);  // 每5秒检查一次进度
                // this.get_oneprogress(task_id)
                console.log(task_dir)
                datatype_change(task_dir).then((res) => {
                    console.log("res", res)
                })
            },
            change_jobs() {
                // let batchSize = this.globalsetting_conf.conversionBatchSize;  // 批次大小
                let batchSize = 3;  // 批次大小
                console.log("batchSize", batchSize)
                if (!this.isConverting) {
                    // 启动转换
                    this.isConverting = true;
                    console.log("开始批量转换...");

                    const startConversion = (job) => {
                        job.converting = true;
                        job.status = "转换中";
                        this.activeConversions++;
                        this.change_job(job.jobdir, job.id); // 启动转换任务
                    };

                    const conversionController = () => {
                        // 检查是否所有任务已完成
                        if (this.jobList.every(job => job.status === "转换完成" || job.status === "转换失败")) {
                            console.log("所有任务已完成转换");
                            this.isConverting = false;
                            return;
                        }

                        // 如果活动转换任务少于批次大小，启动新的转换任务
                        while (this.activeConversions < batchSize) {
                            const nextJob = this.jobList.find(job => job.status !== "转换完成" && !job.converting);
                            if (nextJob) {
                                startConversion(nextJob); // 启动新的转换任务
                            } else {
                                break;
                            }
                        }
                    };

                    // 定时器轮询任务状态
                    const intervalId = setInterval(() => {
                        this.activeConversions = this.jobList.filter(job => job.converting).length;
                        conversionController();

                        // 所有任务完成时清除定时器
                        if (this.jobList.every(job => job.status === "转换完成" || job.status === "转换失败")) {
                            clearInterval(intervalId);
                            this.isConverting = false;
                        }
                    }, 1000);  // 每秒检查一次

                    // 保存定时器ID，以便在必要时暂停转换
                    this.intervalId = intervalId;
                } else {
                    // 暂停转换
                    console.log("暂停转换...");
                    this.isConverting = false;
                    clearInterval(this.intervalId);
                    this.jobList.forEach(job => {
                        if (job.converting) {
                            job.converting = false;
                            this.activeConversions--;
                        }
                    });
                }
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

    .jobs_text {
        width: 65%;
        height: 80px;
        margin-left: 1%;
        float: left;
        display: flex;
        align-items: center;
    }

    .pop-note {
        background-color: #ffffff;
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

    /* From Uiverse.io by KhelVers */
    .button {
        width: 160px;
        height: 50px;
        cursor: pointer;
        font-size: small;
        font-family: inherit;
        font-weight: bold;
        color: #005395;
        background-color: #f8f8fd;
        padding: 0.8em 2.2em;
        border-radius: 10em;
        border: 6px solid #007ABE;
        box-shadow: 0px 6px #004587;
    }

    .button:active {
        position: relative;
        top: 3px;
        border: 6px solid #007ABE;
        box-shadow: 0px 0px;
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
</style>
