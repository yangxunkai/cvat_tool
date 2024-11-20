from flask import Blueprint, request, jsonify
from func.clear_zip_fun import create_ssh_connection, delete_all_jobs, delete_one_job, ssh_close

# 创建一个蓝图
conf_clear_zip = Blueprint('conf_clear', __name__)


#查询所有缓存jobs
@conf_clear_zip.route('/selact_all_jobs', methods=['GET'])
def selectServe():
    data = create_ssh_connection()
    return data

#删除缓存的单个job
@conf_clear_zip.route('/delete_one_job', methods=['GET'])
def delete_onejob():
    data = request.args
    print("data", data)

    # 获取 file_path 参数，修改为 filepath 来与前端一致
    file_path = data.get('filepath', None)

    print("file_path====>", file_path)

    if not file_path:
        return jsonify({"message": "file_path 参数不能为空"}), 400

    result = delete_one_job(file_path)

    return result


#删除缓存所有的job
@conf_clear_zip.route('/delete_all_job', methods=['GET'])
def delete_alljobs():
    data = delete_all_jobs()
    return data
