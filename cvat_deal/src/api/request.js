import axios from 'axios';

// 设置基础 URL
const baseURL = 'http://localhost:5000';

const request = axios.create({
    baseURL,
    timeout: 1000, // 设置请求超时
});

const request1 = axios.create({
    baseURL,
    timeout: 100000000000, // 设置请求超时
});

// 定义获取配置函数
export function obtain_conf() {
    return request.get('/get_conf');
}
// 设置路径等参数
export function set_conf(cookie, class_path, down_save_path, gen_save_path, will_gen_save_path, will_change_path, cvat_ip, serve_username, serve_password, downnum) {
    const formData = new FormData();

    // 只有在参数不为空时才添加到 formData 中
    if (cookie) formData.append('cookie', cookie);
    if (class_path) formData.append('class_path', class_path);
    if (down_save_path) formData.append('down_save_path', down_save_path);
    if (will_gen_save_path) formData.append('will_gen_save_path', will_gen_save_path);
    if (gen_save_path) formData.append('gen_save_path', gen_save_path);
    if (will_change_path) formData.append('will_change_path', will_change_path);
    if (cvat_ip) formData.append('cvat_ip', cvat_ip);
    if (serve_username) formData.append('serve_username', serve_username);
    if (serve_password) formData.append('serve_password', serve_password);
    if (downnum) formData.append('downnum', downnum);

    return request.post('/set_conf', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'  // 设置请求头为 multipart/form-data
        }
    });
}

//选择路径
export function open_dir(type) {
    return request1.get(`/open_dir?type=${type}`);
}

//批量下载接口
export function batch_down(jobids) {
    return request.post('/down_jobs',  jobids
    );
}
//单独下载接口
export function item_down(id) {
    const formData = new FormData();
    formData.append('id', id);
    return request.post('/down_onejob', formData
    );
}
//单独下载状态查看
export function item_down_status(id) {
    return request.get(`/down_onejob_status/${id}`);
}

//cvatssh 连接
export function conn_cvat_ssh() {
    return request1.get('/selact_all_jobs');
}

//删除单个job缓存
export function del_cvat_onejob(filepath) {
    return request1.get(`/delete_one_job?filepath=${filepath}`);
}
//删除所有jobs缓存
export function del_cvat_jobs() {
    return request1.get('/delete_all_job');
}

//解析转换文件夹的子文件夹
export function analysis_changedir(filedir) {
    return request1.get(`/analysis_dir?filedir=${filedir}`);
}

//执行格式转换
export function datatype_change(filedir) {
    return request1.get(`/deal_onechange?change_dir=${filedir}`);
}

//获得转换进度接口
export function get_changeprogress(id) {
    return request1.get(`/get_progress?task_id=${id}`);
}

//开始生成cvat1.1格式
export function start_gencvat(filedir) {
    return request1.get(`/start_gen?filedir=${filedir}`);
}

//获取生成进度接口
export function get_gencvat_progress() {
    return request1.get(`/get_genprogress`);
}
