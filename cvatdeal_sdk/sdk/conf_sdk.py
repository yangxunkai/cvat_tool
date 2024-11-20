from flask import Blueprint, request
from func.conf_fun import obtain_conf, update_conf, open_dir

# 创建一个蓝图
conf_bp = Blueprint('conf', __name__)

#获得设置参数
@conf_bp.route('/get_conf', methods=['GET'])
def get_conf():
    return obtain_conf()

#设置路径参数
@conf_bp.route('/set_conf', methods=['POST'])
def set_conf():
    data = request.form  # 从 POST 请求中获取 JSON 数据
    # 提取各个参数
    cookie = data.get('cookie', '')
    class_path = data.get('class_path', '')
    down_save_path = data.get('down_save_path', '')
    will_gen_save_path = data.get('will_gen_save_path', '')
    gen_save_path = data.get('gen_save_path', '')
    will_change_path = data.get('will_change_path', '')
    cvat_ip = data.get('cvat_ip', '')
    serve_password = data.get('serve_password', '')
    serve_username = data.get('serve_username', '')
    downnum = data.get('downnum', 5)
    return update_conf(cookie, class_path, down_save_path, will_gen_save_path, gen_save_path, will_change_path, cvat_ip, serve_username, serve_password, downnum)

@conf_bp.route('/open_dir', methods=['GET'])
def get_dir():
    data = request.args
    type_name = data.get('type', '')
    return open_dir(type_name)