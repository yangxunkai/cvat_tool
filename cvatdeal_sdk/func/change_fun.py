import argparse
import threading

import cv2
import numpy as np
import paramiko
from flask import jsonify
from tqdm import tqdm
import xml.etree.ElementTree as ET
from func.down_fun import read_conf
import os
import time
#转换状态字典
task_progress = []
#得到其子文件夹
def analysis_dir(file_dir):
    # 存储所有子文件夹路径的列表
    subfolders = []

    try:
        # 遍历给定目录下的所有文件和文件夹
        for item in os.listdir(file_dir):
            # 获取完整的路径
            full_path = os.path.join(file_dir, item)

            # 检查是否是目录
            if os.path.isdir(full_path):
                subfolders.append(full_path)  # 将子文件夹路径添加到列表
        return jsonify({"subfolders": subfolders}), 200

    except Exception as e:
        print(f"读取目录时出错: {str(e)}")
        return jsonify({"subfolders": []}), 200

#cvat格式转yolo分割
classes = ["高风险：警械",
            "高风险：爆炸物",
            "高风险：刀具",
            "高风险：毒害放射物",
            "中风险：限带物",
            "中风险：工具",
            "中风险：打火机",
            "中风险：电池",
            "低风险：液体",
            "高风险：危险液体",
            "低风险：干电池",
            "低风险：易拉罐",
            "中风险：白酒",
            "中风险：香味食品",
            "高风险：电钻",
            "高风险：危险玩具",
            "中风险：压力容器",
            "中风险：喷瓶",
            "高风险：打火机油",
            "低风险：玻璃容器",
            "高风险：固体酒精",
            "高风险：稀料",
            "高风险：子弹",
            "中风险：剪刀",
            "中风险：薄压力容器",
            "高风险：指虎",
            "高风险：金属枪",
            "高风险：手铐",
            "高风险：蓄电池",
            "高风险：香水",
            "中风险：酒精凝胶",
            "中风险：钝器",
            "中风险：火柴",
            "中风险：油漆笔",
            "高风险：打火机器",
            "高风险：自热包"
]
shadow_class = [
    {"in":"毒害放射物", "to":"高风险：毒害放射物"},
    {"in":"指甲油", "to":"中风险：限带物"},
    {"in":"易拉罐", "to":"低风险：易拉罐"},
    {"in":"白酒", "to":"中风险：白酒"},
    {"in":"压力容器", "to":"中风险：压力容器"},
    {"in":"喷瓶", "to":"中风险：喷瓶"},
    {"in":"打火机油", "to":"高风险：打火机油"},
    {"in":"化学试剂", "to":"高风险：稀料"},
    {"in":"薄压力容器", "to":"中风险：薄压力容器"},
    {"in":"香水", "to":"高风险：香水"},
    {"in":"酒精凝胶", "to":"中风险：酒精凝胶"},
    {"in":"塑料容器", "to":"低风险：液体"},
    {"in":"塑料容器", "to":"低风险：液体"},
    {"in":"玻璃容器", "to":"低风险：液体"},
    {"in":"金属容器", "to":"低风险：液体"},
    {"in":"保温杯", "to":"低风险：液体"},
    {"in":"塑料油桶", "to":"高风险：危险液体"},
    {"in":"高风险：警棍", "to":"高风险：警械"},
    {"in":"中风险：锤子", "to":"中风险：工具"},
    {"in":"高风险：爆竹", "to":"高风险：爆炸物"},
    {"in":"中风险：花露水", "to":"中风险：限带物"},
    {"in":"中风险：染发剂", "to":"中风险：限带物"},
    {"in":"高风险：打火机气", "to":"中风险：压力容器"},
    {"in":"高风险：镁棒", "to":"中风险：工具"},
    {"in":"高风险：压缩气体", "to":"中风险：压力容器"},
    {"in":"中风险：无火香薰", "to":"高风险：危险液体"},
    {"in":"高风险：冷烟花", "to":"高风险：爆炸物"},
    {"in":"高风险：双飞人", "to":"中风险：限带物"},
]
def get_shadow_class(name):
    final_name = ""
    for class_one in shadow_class:
        if name == class_one["in"]:
            final_name = class_one["to"]
            break  # 找到匹配项后直接退出循环
        else:
            final_name = name

    return  final_name
def cvat_xml_2_txt(parse_xml_file, save_path, task_id):
    save_path = save_path + "/"
    tree = ET.parse(parse_xml_file)
    root = tree.getroot()
    total_images = len(root.findall('.//image'))
    # 查找每个图像及其对应的掩码
    for idx, image in enumerate(tqdm(root.findall('.//image'), total=total_images)):
        progress = (idx + 1) * 100 // total_images / 2
        if progress<50:
            status = "转换中"
        else:
            status = "格式完成"
        update_progress(task_id, progress, status)
        # 获取图像的名称
        image_name = image.get('name')
        # 去掉文件扩展名
        image_name_without_extension = os.path.splitext(image_name)[0]

        # 获取图像的宽高
        image_width = int(image.get('width'))
        image_height = int(image.get('height'))

        dw = 1. / image_width
        dh = 1. / image_height

        os.makedirs(save_path, exist_ok=True)

        with open(os.path.join(save_path + image_name_without_extension + '.txt'), 'w') as f:
            for polygon in image.findall('.//polygon'):
                polygon_label = polygon.get('label')
                polygon_points = polygon.get('points')

                polygon_label = get_shadow_class(polygon_label)
                # print("polygon_label", polygon_label)

                if polygon_label not in ["_background_", "__ignore__", "液体区域"]:
                    # 删除末尾的分号，并使用分号分割数据对
                    pairs_points = polygon_points.replace(";", ",")
                    # 将字符串转换为浮点数列表
                    points_list = [float(point) for point in pairs_points.split(",")]
                    poly = [dw * x if i % 2 == 0 else dh * x for i, x in enumerate(points_list)]
                    class_num = classes.index(polygon_label)
                    line = str(class_num) + " " + " ".join(map(str, poly)) + ' '
                    line = line.rstrip()  # 去掉末尾的空格

                    # f.write(str(class_num) + " " + " ".join(map(str, poly)) + ' ')
                    f.write(line + '\n')  # 在循环结束后添加换行符
                else:
                    pass
        time.sleep(0.1)

#分割轮廓转矩形框
def parse_polygon_data(label):
    """
    解析多边形数据。
    :param label: 包含类别编号和多边形坐标的字符串
    :return: 类别编号和多边形坐标
    """
    parts = label.split()
    class_id = int(parts[0])
    poly = np.array(parts[1:], dtype=np.float32).reshape(-1, 2)  # Read poly, reshape

    return class_id, poly

def convert_polygon_to_bbox(polygon):

    """
    从多边形计算边界框。
    :param polygon: 多边形的点列表 [[x1, y1], [x2, y2], ...]
    :return: 边界框 (x_center, y_center, width, height)
    """
    x_min = np.min(polygon[:, 0])
    y_min = np.min(polygon[:, 1])
    x_max = np.max(polygon[:, 0])
    y_max = np.max(polygon[:, 1])

    width = x_max - x_min
    height = y_max - y_min
    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0

    return x_center, y_center, width, height

def convert_to_yolo_format(image_width, image_height, bbox):
    """
    将边界框转换为YOLO格式。
    :param image_width: 图像宽度
    :param image_height: 图像高度
    :param bbox: 边界框 (x_center, y_center, width, height)
    :return: YOLO格式 (x_center_rel, y_center_rel, width_rel, height_rel)
    """
    x_center, y_center, width, height = bbox
    x_center_rel = int(x_center) / image_width
    y_center_rel = int(y_center) / image_height
    width_rel = int(width) / image_width
    height_rel = int(height) / image_height

    return x_center_rel, y_center_rel, width_rel, height_rel

def convert_segmentation_to_detection(image_path, label_path, output_dir):
    """
    将分割数据转换为检测数据。
    :param image_path: 图像文件路径
    :param label_path: 标签文件路径
    :param output_dir: 输出目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    with open(label_path, 'r') as f:
        labels = f.read().splitlines()

    output_file = os.path.join(output_dir, os.path.basename(label_path))
    with open(output_file, 'w') as f:
        for label in labels:
            class_id, poly = parse_polygon_data(label)
            # poly *= [w, h]  # Unscale to image size
            poly = poly.tolist()
            poly = np.array(poly) * [w, h]

            bbox = convert_polygon_to_bbox(poly)
            yolo_bbox = convert_to_yolo_format(w, h, bbox)
            yolo_label = f"{class_id} " + " ".join(map(str, yolo_bbox)) + "\n"
            f.write(yolo_label)

def process_folder(image_dir, label_dir, output_dir, task_id):
    """
    遍历文件夹中的图像和标签文件，并调用转换函数处理每个图像。
    :param image_dir: 包含图像文件的目录
    :param label_dir: 包含标签文件的目录
    :param output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在

    image_extensions = ['.png', '.jpg', '.jpeg']  # 图像文件扩展名列表
    total_num = len(os.listdir(label_dir))
    for idx, label_filename in enumerate(tqdm(os.listdir(label_dir), total=total_num)):
        if not label_filename.endswith('.txt') or label_filename=='classes.txt':
            continue

        # 构建图像和标签文件的完整路径
        label_path = os.path.join(label_dir, label_filename)

        # 获取图像文件名（假设与标签文件同名，但可能有不同的扩展名）
        image_basename = os.path.splitext(label_filename)[0]
        image_path = None

        # 在图像目录中查找对应的图像文件
        for ext in image_extensions:
            potential_image_path = os.path.join(image_dir, image_basename + ext)
            if os.path.exists(potential_image_path):
                image_path = potential_image_path
                break

        if image_path is None:
            print(f"未找到与标签文件 '{label_filename}' 相关联的图像文件。")
            continue

        # 调用转换函数处理单个图像和标签
        convert_segmentation_to_detection(image_path, label_path, output_dir)
        progress = 50 + (idx + 1) * 100 // total_num / 2
        if progress<100:
            status="生成中"
            update_progress(task_id, progress, status)
        else:
            status="已完成"
            global task_progress
            task_progress = [task for task in task_progress if task['id'] != task_id]


#单个处理
def deal_one(full_path):
    task_id = int(full_path.split('job_')[1].split('_dataset')[0])
    start_task(task_id)
    if not check_changed(full_path):
        # 检查是否是目录
        if os.path.isdir(full_path):
            # 检查子目录下的 'images' 目录
            # 如果有图像数据，不用find打开下列两行注释以及第四行，注释第三行
            images_dir = os.path.join(full_path, 'images')
            if os.path.isdir(images_dir):
                # if True:
                img_path = images_dir
                # print(f"Images directory: {images_dir}")

                # 创建'sgelabels'和'labels'目录
                sgelabels_path = os.path.join(full_path, 'sgelabels')
                labels_path = os.path.join(full_path, 'labels')

                os.makedirs(sgelabels_path, exist_ok=True)
                os.makedirs(labels_path, exist_ok=True)

            # 检查子目录下的 'annotations.xml' 文件
            annotations_file = os.path.join(full_path, 'annotations.xml')
            if os.path.isfile(annotations_file):
                Ann_path = annotations_file

        # 先转为YOLO分割标签 若已经有了分割标签就直接注释这行
        cvat_xml_2_txt(Ann_path, sgelabels_path, task_id)
        # 将YOLO分割标签转为YOLO矩形框
        process_folder(img_path, sgelabels_path, labels_path, task_id)
    else:
        update_progress(task_id, 100, "已完成")
    return jsonify({"message": f"执行成功!"}), 200

# 启动一个新的任务并加入进度列表
def start_task(task_id):
    print("进度开始", task_id)
    task_info = {
        "id": task_id,
        "progress": 0,
        "status": "开始"  # 初始状态为 pending
    }
    task_progress.append(task_info)

# 更新指定任务的进度
def update_progress(task_id, progress, status):
    for task in task_progress:
        if task["id"] == task_id:
            task["progress"] = progress
            task["status"] = status

def get_progress(task_id):
    print("task_progress", task_progress)
    for task in task_progress:
        if task['id'] == task_id:
            print("task", task)
            # 找到对应的任务 ID，返回任务的进度和状态
            return task
        # 如果没有找到，返回空字典
    return {}

#验证是否已转换
def check_changed(file_dir):
    imagesnum = len(os.listdir(os.path.join(file_dir, "images")))
    if os.path.isdir(os.path.join(file_dir, "labels"))==False and os.path.isdir(os.path.join(file_dir, "labels"))==False:
        return False

    if len(os.listdir(os.path.join(file_dir, "labels")))==imagesnum and len(os.listdir(os.path.join(file_dir, "sgelabels")))==imagesnum:
        return True
    else:
        return False

if __name__ == '__main__':
    # 示例调用
    file_dir = r"D:\2\cvat"  # 请替换为你想读取的目录路径
    file_dir_one = r"D:\2\cvat\job_790_dataset_2024_09_27_10_29_11_cvat for images 1.1"
    # # subfolders = analysis_dir(file_dir)
    # # print(subfolders)
    # # 创建两个线程
    # thread_1 = threading.Thread(target=deal_one, args=(file_dir_one,))
    # thread_2 = threading.Thread(target=get_progress, args=(790,))
    #
    # # 启动线程
    # thread_1.start()
    # thread_2.start()
    #
    # # 等待线程完成
    # thread_1.join()
    # thread_2.join()
    #
    # print("Both tasks are complete.")
    print(check_changed(file_dir_one))