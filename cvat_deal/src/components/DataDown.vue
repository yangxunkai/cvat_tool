<template>
    <div class="card">
        <div class="bg">
            <div class="jobs_text">
                <n-popover trigger="hover">
                    <template #trigger>
                        <n-button type="info" dashed class="title_btn">
                            工作ID:
                        </n-button>
                    </template>
                    <span>
                        <n-alert title="注意：" class="pop-note" type="warning" :bordered="false">
                            内容格式: 例如1,2,3 (中间使用逗号分割, 或者直接4-6)
                        </n-alert>
                    </span>
                </n-popover>
                <n-input
                        type="textarea"
                        v-model:value="jobs"
                        class="input_value"
                        placeholder="例如1,2,3 (中间使用逗号分割, 或者直接4-6)"
                        round clearable>
                </n-input>
            </div>
            <n-divider :vertical="true" class="divier_line"/>
            <div class="jobs_btn">
                <button class="animated-button" @click="jobs_analysis()">
                    <svg xmlns="http://www.w3.org/2000/svg" class="arr-2" viewBox="0 0 24 24">
                        <path
                                d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
                        ></path>
                    </svg>
                    <span class="text">解析</span>
                    <span class="circle"></span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="arr-1" viewBox="0 0 24 24">
                        <path
                                d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
                        ></path>
                    </svg>
                </button>
            </div>

        </div>
        <!--        <div class="blob"></div>-->
    </div>
    <n-divider/>
    <n-button strong round :type="isDownloading ? 'error' : 'success'" @click="download_jobs()">
        {{ isDownloading ? '暂停' : '下载全部' }}
    </n-button>

    <!--    解析下载表格-->
    <div class="table-content">
        <n-space vertical>
            <n-table virtual-scroll type="selection" striped>

                <thead>
                <tr>
                    <th>ID:</th>
                    <th>状态:</th>
                    <th>下载进度:</th>
                    <th style="text-align: center">操作</th>
                </tr>
                </thead>
                <tbody>
                <tr :v-if="jobList.length>0" v-for="job in jobList" :key="job.id">
                    <td>{{ job.id }}</td>
                    <td>
                        <n-tag :bordered="false"
                               :type="job.status === '下载完成' ? 'success':job.status === '下载中' ? 'info' : job.status === '打包中' ? 'warning' : 'error'">
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
                        <n-button type="success" class="down_btn" @click="download_job(job.id)">
                            <template v-if="job.down_loading">
                                <n-spin size="small" stroke="#ffffff">
                                </n-spin>
                            </template>
                            <div v-else class="load_style">
                                <div style="align-items: center; height: 100%;margin-top: 20%">
                                    下载
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
    import {item_down, item_down_status} from "@/api/request"; // 导入请求方法
    import {changeColor} from 'seemly'
    import {useThemeVars} from 'naive-ui'
    import {SyncCircleOutline} from "@vicons/ionicons5";
    import {mapState} from "vuex";

    export default defineComponent({
        name: 'DataDownComponent',
        data() {
            return {
                jobs: "827,828,817,818,620-630,950-952,991,933,954,955,915,916,1003,1004,1002,923,947,924-926,948-949,609",
                jobList: [],
                jobids: [],
                changeColor,
                themeVars: useThemeVars(),
                spin_show: false,
                isDownloading: false,  // 控制下载状态
                activeDownloads: 0,    // 当前活动下载数量
            };
        },
        mounted() {

        },
        components: {
            SyncCircleOutline
        },
        computed: {
            ...mapState(['globalsetting_conf']) // 从 Vuex 获取全局状态
        },
        methods: {
            jobs_analysis() {
                this.jobList = []
                this.jobids = []
                // 解析输入
                const ids = this.jobs.split(',').map(id => id.trim());

                if (ids.length > 0) {
                    for (let i = 0; i < ids.length; i++) {
                        if (ids[i].split('-').length > 1) {
                            for (let j = parseInt(ids[i].split('-')[0]); j <= parseInt(ids[i].split('-')[1]); j++) {
                                this.jobList.push(
                                    {
                                        id: j.toString(),
                                        status: "待操作",
                                        progress: 0,
                                        down_loading: false
                                    }
                                )
                            }
                        } else {
                            this.jobList.push(
                                {
                                    id: ids[i],
                                    status: "待操作",
                                    progress: 0,
                                    down_loading: false
                                }
                            )
                        }
                    }
                } else {
                    this.jobList = []
                }
                this.jobList.sort((a, b) => a.id - b.id);
                this.jobList.map((job_item) => {
                    this.jobids.push(job_item.id)
                })
                console.log("ids", this.jobList.map((item) => {
                    return item.id
                }).join(','))
            },
            download_jobs() {
                let batchSize = this.globalsetting_conf.downnum;  // 批次大小
                // console.log("开始批量下载，单批次大小:", batchSize);

                if (!this.isDownloading) {
                    // 启动下载
                    this.isDownloading = true;
                    console.log("开始下载...");

                    // 批量下载控制器
                    const startDownload = (job) => {
                        job.down_loading = true;
                        this.activeDownloads++;
                        this.download_job(job.id); // 调用下载任务
                    };

                    // 批量下载控制器
                    const downloadController = () => {
                        if (this.jobList.every(job => job.status === "下载完成" || job.status === "打包失败")) {
                            console.log("所有任务下载完成");
                            this.isDownloading = false;  // 所有任务完成时停止下载
                            return;
                        }

                        // 当活动下载任务少于批次大小时，触发新的下载任务
                        while (this.activeDownloads < batchSize) {
                            const nextJob = this.jobList.find(job => job.status !== "下载完成" && !job.down_loading);
                            if (nextJob) {
                                startDownload(nextJob); // 触发下载任务
                            } else {
                                break; // 没有新任务时退出循环
                            }
                        }
                    };

                    // 监听每个任务状态的变化
                    const intervalId = setInterval(() => {
                        this.activeDownloads = this.jobList.filter(job => job.down_loading).length;
                        downloadController(); // 控制器检查是否需要下载新任务

                        // 若所有任务完成，停止定时器
                        if (this.jobList.every(job => job.status === "下载完成" || job.status === "打包失败")) {
                            clearInterval(intervalId);
                            this.isDownloading = false;
                        }
                    }, 2000); // 每2秒检查一次

                    // 保存定时器ID
                    this.intervalId = intervalId;
                } else {
                    // 暂停下载
                    console.log("暂停下载...");
                    this.isDownloading = false;
                    clearInterval(this.intervalId); // 停止定时器
                    this.jobList.forEach(job => {
                        if (job.down_loading) {
                            job.down_loading = false;  // 停止正在下载的任务
                            this.activeDownloads--; // 减少活动下载数
                        }
                    });
                }
            },

            download_job(id) {
                this.jobList.map((item) => {
                    if (item.id === id) {
                        item.down_loading = true;
                    }
                })
                //出发打包和下载
                item_down(id)
                // 设置定时器，每2秒查询一次状态
                const intervalId = setInterval(() => {
                    console.log("id", id)

                    item_down_status(id)
                        .then(response => {
                            this.down_loading = false
                            const status = response.data.state;  // 获取任务状态
                            const progress = response.data.progress
                            console.log("this.jobList", this.jobList)
                            if (status === "下载完成") {
                                this.jobList.map((item) => {
                                    if (item.id === id) {
                                        item.down_loading = false;
                                        item.status = status;
                                        item.progress = 100
                                    }
                                })
                            } else {
                                this.jobList.map((item) => {
                                    if (item.id === id) {
                                        item.status = status;
                                        if (status === "打包中") {
                                            this.spin_show = true
                                        } else if (this.spin_show === true) {

                                            this.spin_show = false
                                        } else if (status === "打包失败") {
                                            item.down_loading = false;
                                            this.spin_show = false
                                            alert("Cookie失效，请先检查Cookie值！！")
                                        }
                                        item.progress = response.data.progress
                                    }
                                })
                            }
                            // 如果任务完成或失败，清除定时器
                            if (status === "下载完成" || status === "打包失败") {
                                console.log(`任务 ${id} ${status}，销毁定时器`);
                                clearInterval(intervalId);
                            } else {
                                console.log(`任务 ${id} 当前状态: ${status} 下载进度: ${progress}`);
                            }
                        })
                        .catch(error => {
                            console.error(`查询任务 ${id} 状态失败:`, error);
                            clearInterval(intervalId);  // 如果查询状态失败，也销毁定时器
                        });
                }, 2000);  // 每2秒查询一次
            }
        }
    });

</script>

<style scoped>
    /* From Uiverse.io by dylanharriscameron */
    .card {
        position: relative;
        width: 60%;
        height: 200px;
        border-radius: 14px;
        z-index: 1111;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff;;
        margin-left: 20%;
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
        height: 200px;
        margin-left: 5%;
        float: left;
    }

    .pop-note {
        background-color: #ffffff;
    }

    .title_btn {
        margin-top: 1.5%;
        color: #005193
    }

    .divier_line {
        height: 200px;
    }

    .jobs_btn {
        height: 200px;
        display: flex;
        align-items: center;
        width: 20%;
        float: right;
    }

    .input_value {
        height: 60%;
        margin-top: 2%;
        text-align: left;
    }

    /* From Uiverse.io by ryota1231 */
    .animated-button {
        position: relative;
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 16px 36px;
        border: 4px solid;
        border-color: transparent;
        font-size: 16px;
        border-radius: 100px;
        font-weight: 600;
        color: #1f387e;
        box-shadow: 0 0 0 2px #ffffff;
        cursor: pointer;
        overflow: hidden;
        transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button svg {
        position: absolute;
        width: 24px;
        fill: #1f387e;
        z-index: 9;
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button .arr-1 {
        right: 16px;
    }

    .animated-button .arr-2 {
        left: -25%;
    }

    .animated-button .circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        background-color: #c5e5e4;
        border-radius: 50%;
        opacity: 0;
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button .text {
        position: relative;
        z-index: 1;
        transform: translateX(-12px);
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button:hover {
        box-shadow: 0 0 0 12px transparent;
        color: #212121;
        border-radius: 12px;
    }

    .animated-button:hover .arr-1 {
        right: -25%;
    }

    .animated-button:hover .arr-2 {
        left: 16px;
    }

    .animated-button:hover .text {
        transform: translateX(12px);
    }

    .animated-button:hover svg {
        fill: #1f387e;
    }

    .animated-button:active {
        scale: 0.95;
        box-shadow: 0 0 0 4px #005193;
    }

    .animated-button:hover .circle {
        width: 220px;
        height: 220px;
        opacity: 1;
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
        width: 80%;
    }

    .down_btn {
        width: 80px;
        height: 40px;
    }

    .load_style {
        height: 30px;
        align-items: center;
        padding-top: 6px;
    }
</style>
