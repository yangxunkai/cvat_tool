import threading

from flask import Blueprint, request, jsonify
from func.down_fun import batch_down, item_down, status_dict

# 创建一个蓝图
down_bp = Blueprint('down', __name__)

#批量下载jobs
@down_bp.route('/down_jobs', methods=['POST'])
def batch_downing():
    data = request.form
    joblist = data.get('joblist', '')
    print("joblist", joblist)
    return batch_down(joblist)

#单独下载job
@down_bp.route('/down_onejob', methods=['POST'])
def item_downing():
    data = request.form
    id = data.get('id', '')
    print("id", id)

    # 启动一个线程进行打包和下载
    threading.Thread(target=item_down, args=(id,)).start()

    return jsonify({"message": "打包和下载已开始", "id": id}), 202

# 获取下载状态
@down_bp.route('/down_onejob_status/<int:id>', methods=['GET'])
def get_status(id):
    if str(id) in status_dict:
        return jsonify(status_dict[str(id)]), 200
    else:
        return jsonify({"error": "无效的ID"}), 404