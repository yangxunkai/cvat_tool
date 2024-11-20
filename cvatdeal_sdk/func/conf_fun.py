from flask import jsonify
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget
from PyQt5.QtCore import Qt
import sys
import json
import os

"""获得设置参数"""
def obtain_conf():
    conf_data = {
        "cookie": "",
        "class_path": "",
        "down_save_path": "",
        "will_gen_save_path": "",
        "gen_save_path": "",
        "will_change_path": "",
        "cvat_ip": "",
        "serve_username": "",
        "serve_password": "",
        "downnum": 5
    }
    #若配置文件不存在，则生成配置文件
    if not os.path.exists('./conf.json'):
        with open('./conf.json', 'w') as conf:
            json.dump(conf_data, conf, indent=4)
    try:
        with open('./conf.json', 'r') as conf:
            conf_json = json.load(conf)
            return jsonify(conf_json), 200
    except:
        return jsonify({"message": "参数查询失败！"}), 404

"""写入设置参数"""
def update_conf(cookie, class_path, down_save_path, will_gen_save_path, gen_save_path, will_change_path, cvat_ip, serve_username, serve_password, downnum):
    # 读取现有配置
    try:
        with open('./conf.json', 'r') as conf:
            conf_json = json.load(conf)
    except FileNotFoundError:
        conf_json = {}  # 如果文件不存在，初始化一个空字典

    # 用字典存储传入的参数
    updates = {
        'cookie': cookie,
        'class_path': class_path,
        'down_save_path': down_save_path,
        'will_gen_save_path': will_gen_save_path,
        'gen_save_path': gen_save_path,
        'will_change_path': will_change_path,
        'cvat_ip': cvat_ip,
        'serve_username': serve_username,
        'serve_password': serve_password,
        'downnum': int(downnum)
    }

    # 遍历字典，更新非空参数
    for key, value in updates.items():
        if value:  # 如果 value 不是空字符串，则更新
            conf_json[key] = value

    # 写入更新后的配置
    with open('./conf.json', 'w') as conf:
        json.dump(conf_json, conf, indent=4)  # 使用 indent=4 以便格式化输出
    try:
        result = {
            "data": conf_json,
            "message": "更新成功！"
        }
        return jsonify(result), 200
    except:
        jsonify({"message": "更新错误！"}), 404

"""选择文件夹（使用 PyQt5）"""
def open_dir(type_name):
    try:
        # 创建 PyQt5 的应用程序（如果已经存在，则不再创建）
        qt_app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)

        widget = QWidget()
        widget.setWindowTitle('选择文件夹' if type_name != 'class' else '选择文件')
        widget.setWindowModality(Qt.ApplicationModal)  # 设置为应用程序模态，确保在最上层

        # 使文件选择对话框在最上层
        widget.setWindowFlags(Qt.WindowStaysOnTopHint)  # 保持窗口在最上层

        if type_name == 'class_path':
            # 打开文件选择对话框，仅允许选择 .txt 文件
            file_path, _ = QFileDialog.getOpenFileName(widget, "选择 .txt 文件", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                result = {
                    "folder_path": file_path,
                    "type": type_name,
                    "code": 201,
                    "message": "文件选择成功！"
                }
            else:
                result = {
                    "type": type_name,
                    "code": 202,
                    "message": "未选择文件！"
                }
        else:
            # 打开文件夹选择对话框
            folder_path = QFileDialog.getExistingDirectory(widget, "选择文件夹")
            if folder_path:
                result = {
                    "folder_path": folder_path,
                    "type": type_name,
                    "code": 201,
                    "message": "文件夹选择成功！"
                }
            else:
                result = {
                    "type": type_name,
                    "code": 202,
                    "message": "未选择文件夹！"
                }

        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"type": type_name, "message": "选择失败！"}), 404