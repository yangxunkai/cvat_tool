from flask import Blueprint, request, jsonify
from func.gen_fun import start_gen_task, get_genprogress

# 创建一个蓝图
gen_cvat = Blueprint('gen_cvat', __name__)


#查询所有缓存jobs
@gen_cvat.route('/start_gen', methods=['GET'])
def start_gen():
    data = request.args
    filedir = data.get('filedir', None)
    print("filedir", filedir)
    result = start_gen_task(filedir)
    return result

#进行格式转换
@gen_cvat.route('/get_genprogress', methods=['GET'])
def genprogress():
    result = get_genprogress()
    return result


