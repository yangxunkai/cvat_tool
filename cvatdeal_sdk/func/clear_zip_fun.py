import paramiko
from flask import jsonify

from func.down_fun import read_conf

#连接ssh
def create_ssh_connection():
    json_conf = read_conf()
    remote_host = json_conf["cvat_ip"]
    username = json_conf["serve_username"]
    password = json_conf["serve_password"]

    """建立 SSH 连接并返回 SSH 客户端对象"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥
    command = "find ~/share/data -name 'export_cache' -type d -exec find {} -type f -name '*.ZIP' \\;"

    try:
        # 连接到远程主机
        ssh.connect(remote_host, username=username, password=password)
        print(f"成功连接到 {remote_host}")

        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)

        # 获取命令输出和错误
        output = stdout.read().decode()
        error = stderr.read().decode()

        # 如果有输出
        if output:
            print("找到的 ZIP 文件：")
            out_list = []
            for out_item in output.split('\n'):
                if out_item != "":
                    out_list.append({
                        "jobId": out_item.split("/")[6],
                        "jobName": out_item
                    })
            print(out_list)
            ssh_close(ssh)
            return jsonify({"message": "查询成功！", "output": out_list}), 200

        # 如果没有找到文件，但没有错误
        if not output and not error:
            ssh_close(ssh)
            return jsonify({"message": "没有找到 ZIP 文件", "output": []}), 200

        # 如果有错误信息
        if error:
            print("错误信息：")
            print(error)
            ssh_close(ssh)
            return jsonify({"message": "查找失败！", "error": error}), 204

    except Exception as e:
        print(f"SSH 连接失败: {str(e)}")
        return None

#删除所有的jobs
def delete_all_jobs():
    """删除所有 'export_cache' 目录中的 ZIP 文件"""
    json_conf = read_conf()
    remote_host = json_conf["cvat_ip"]
    username = json_conf["serve_username"]
    password = json_conf["serve_password"]

    """建立 SSH 连接并返回 SSH 客户端对象"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥
    # 连接到远程主机
    ssh.connect(remote_host, username=username, password=password)
    if ssh is None:
        print("SSH 连接无效，无法执行命令。")
        return

    # 定义删除所有 .ZIP 文件的命令
    command = "find ~/share/data -name 'export_cache' -type d -exec sh -c 'find \"$0\" -type f -name \"*.ZIP\" -delete' {} \\;"

    try:
        # 执行删除命令
        stdin, stdout, stderr = ssh.exec_command(command)

        # 获取命令输出和错误
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh_close(ssh)
        # 打印结果
        if output:
            print("删除所有 ZIP 文件：")
            print(output)
        if error:
            print("错误信息：")
            print(error)
        else:
            # print("所有 ZIP 文件已成功删除。")
            return jsonify({"message": "所有 ZIP 文件已成功删除。"}), 200

    except Exception as e:
        ssh_close(ssh)
        print(f"执行删除命令时出错: {str(e)}")
        return jsonify({"message": f"执行删除命令时出错: {str(e)}"}), 404

#删除特定的job
def delete_one_job(file_path):
    print("file_path", file_path)
    """删除指定路径的 ZIP 文件"""
    json_conf = read_conf()
    remote_host = json_conf["cvat_ip"]
    username = json_conf["serve_username"]
    password = json_conf["serve_password"]

    # 建立 SSH 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥

    try:
        # 连接到远程主机
        ssh.connect(remote_host, username=username, password=password)
        print(f"成功连接到 {remote_host}")

        # 定义直接删除文件的命令
        command = f"rm -f {file_path}"

        # 执行删除命令
        stdin, stdout, stderr = ssh.exec_command(command)

        # 获取命令输出和错误
        output = stdout.read().decode()
        error = stderr.read().decode()

        # 关闭 SSH 连接
        ssh_close(ssh)

        # 打印结果
        if output:
            print(f"删除文件 {file_path}：")
            print(output)
        if error:
            print("错误信息：")
            print(error)
            return jsonify({"message": f"删除文件时发生错误: {error}"}), 500
        else:
            print(f"{file_path} 文件已成功删除。")
            return jsonify({"message": f"{file_path} 文件已成功删除。"}), 200

    except paramiko.AuthenticationException:
        print(f"SSH 认证失败，无法连接到 {remote_host}")
        return jsonify({"message": f"SSH 认证失败，无法连接到 {remote_host}"}), 401
    except paramiko.SSHException as e:
        print(f"SSH 连接失败: {str(e)}")
        return jsonify({"message": f"SSH 连接失败: {str(e)}"}), 500
    except Exception as e:
        print(f"执行删除命令时出错: {str(e)}")
        return jsonify({"message": f"执行删除命令时出错: {str(e)}"}), 404
#断开连接
def ssh_close(ssh_client):
    ssh_client.close()

if __name__ == '__main__':
    #查询jobs
    # create_ssh_connection()
    #删除某个job
    delete_one_job("/home/cvat/share/data/jobs/620/export_cache/dataset_cvat-for-images-11.ZIP")