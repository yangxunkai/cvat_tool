from flask import Blueprint, request, jsonify
from func.change_fun import analysis_dir, deal_one, get_progress

# 创建一个蓝图
conf_change = Blueprint('conf_change', __name__)


#查询所有缓存jobs
@conf_change.route('/analysis_dir', methods=['GET'])
def get_analysis_dir():
    data = request.args
    filedir = data.get('filedir', None)
    print("filedir", filedir)
    result = analysis_dir(filedir)
    return result

#进行格式转换
@conf_change.route('/deal_onechange', methods=['GET'])
def deal_onechange():
    data = request.args
    file_dir = data.get('change_dir', None)
    if file_dir:
        result = deal_one(file_dir)
    else:
        result = jsonify({"message": f"路径为空，执行错误！"}), 404
    return result

#查询格式转换进程
@conf_change.route('/get_progress', methods=['GET'])
def get_oneprogress():
    data = request.args
    task_id = int(data.get('task_id', None))
    task = get_progress(task_id)
    if  task=={} or task['progress']==100:
        message = "转换完成！"
    else:
        message = "正在转换！"
    return jsonify({"message": message, "task": task}), 200


