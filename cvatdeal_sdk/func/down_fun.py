import json
import os
import re
import requests
import time
from flask import jsonify
from tqdm import tqdm
from threading import Thread

# 用于存储状态和进度的字典
status_dict = {}

#读取参数
def read_conf():
    with open('./conf.json', 'r') as conf:
        conf_json = json.load(conf)
    return conf_json

#开始打包
def start_pack(pack_url, cookie):
    headers = {
        "Cookie": cookie,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "192.168.100.252:8080",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.get(pack_url, headers=headers)
    if response.status_code == 202:
        return "打包中"
    elif response.status_code == 201:
        return "打包完成"
    else:
        print("请求失败，状态码:", response.status_code)
        return None

# 下载文件
def start_down(url, save_path, headers, job_id):
    max_retries = 3
    attempt = 0
    response = None

    # 重试下载
    while attempt < max_retries:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            break
        attempt += 1
        print(f"尝试 {attempt} 失败，状态码: {response.status_code}")

    # 下载失败处理
    if response is None or response.status_code != 200:
        status_dict[job_id]["state"] = "下载失败"
        return jsonify({"error": "下载失败", "status_code": response.status_code if response else "无响应"}), response.status_code if response else 500

    # 获取文件名和文件大小
    content_disposition = response.headers.get('content-disposition', '')
    file_name_match = re.search(r'filename="([^"]+)"', content_disposition)
    if file_name_match:
        file_name = file_name_match.group(1)
    else:
        file_name = f'downloaded_file_{job_id}.zip'  # 如果没有提供文件名，使用默认文件名

    file_path = os.path.join(save_path, file_name)
    remote_file_size = int(response.headers.get('content-length', 0))

    # 检查文件是否已经下载过，并比较文件大小
    if os.path.exists(file_path):
        local_file_size = os.path.getsize(file_path)
        if local_file_size == remote_file_size:
            print(f"文件 {file_name} 已经下载过且完整，跳过下载。")
            status_dict[job_id]["state"] = "下载完成"
            return
        else:
            print(f"文件 {file_name} 已存在但大小不匹配，重新下载。")

    # 开始下载文件
    downloaded = 0
    status_dict[job_id]["state"] = "下载中"
    print(f"任务 {job_id} 下载中，文件: {file_name}...")

    # 使用 tqdm 显示下载进度条
    with open(file_path, 'wb') as f, tqdm(total=remote_file_size, unit='B', unit_scale=True, desc=f"任务 {job_id}") as pbar:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                pbar.update(len(chunk))
                # 更新进度
                status_dict[job_id]["progress"] = int(downloaded / remote_file_size * 100)

    if status_dict[job_id]["progress"] == 100:
        status_dict[job_id]["state"] = "下载完成"
    print(f"任务 {job_id} 下载完成，文件已保存至 {file_path}")

#单独下载
def item_down(id):
    json_conf = read_conf()
    cookie = json_conf["cookie"]
    cvat_ip = json_conf["cvat_ip"]
    down_save_path = json_conf["down_save_path"]
    pack_url = f'http://{cvat_ip}:8080/api/jobs/{id}/dataset?org=&use_default_location=true&format=CVAT+for+images+1.1'
    download_url = pack_url + '&action=download'
    print("pack_url", pack_url)

    headers = {
        "Cookie": cookie,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "192.168.100.252:8080",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    # 设置初始状态
    status_dict[id] = {"state": "打包中", "progress": 0}

    # 轮询打包状态
    for _ in range(30):  # 最多查询 30 次
        pack_status = start_pack(pack_url, cookie)
        if pack_status == "打包完成":
            status_dict[id]["state"] = "下载中"
            # 开始下载
            start_down(download_url, down_save_path, headers, id)
            break
        elif pack_status == "打包中":
            time.sleep(1)  # 等待 10 秒
        else:
            status_dict[id]["state"] = "打包失败"
            return None
#批量下载
def batch_down(job_list):

    json_conf = read_conf()
    cookie = json_conf["cookie"]
    save_path = json_conf["down_save_path"]
    cvat_ip = json_conf["cvat_ip"]

    headers = {
        "Cookie": cookie,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": "192.168.100.252:8080",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    pack_urls = []
    for id in job_list:
        pack_url = f'{cvat_ip}/api/jobs/{id}/dataset?org=&use_default_location=true&format=CVAT+for+images+1.1'
        pack_urls.append(pack_url)

    # 记录正在打包的任务
    packing_status = {url: False for url in pack_urls}

    # 开始打包
    while packing_status:
        for pack_url in list(packing_status.keys()):
            status = start_pack(pack_url, cookie)
            if status == "打包完成":
                print("job" + pack_url.split('jobs/')[1].split('/dataset')[0], "打包完成，开始下载...")
                Thread(target=start_down, args=(pack_url + '&action=download', save_path, headers)).start()
                packing_status.pop(pack_url)
            elif status == "打包中":
                print("job" + pack_url.split('jobs/')[1].split('/dataset')[0], "打包中，请稍候...")
        time.sleep(1)

    print("所有任务已处理完毕")

if __name__ == '__main__':
    json_conf = read_conf()
    cookie = json_conf["cookie"]
    down_save_path = json_conf["down_save_path"]
    print("cookie", "down_save_path", cookie, down_save_path)
    # save_path = "D:\\2"
    # joblist_path = 'joblist.txt'
    # batch_down(joblist_path, save_path, cookie)