import argparse
import xml.etree.ElementTree as ET

from flask import jsonify
from tqdm import tqdm
from xml.dom import minidom
import os
import imagesize
import random
import threading

gen_status = {
    "progress": 0,
    "status": "未操作"
}

# 生成CVAT 1.1格式
def gen_cvat1_1(dataset_path):
    global gen_status
    gen_status = {
        "progress": 0,
        "status": "开始"
    }
    dataset_image = os.path.join(dataset_path, 'images')
    dataset_yolo = os.path.join(dataset_path, 'labels')
    dataset_cvat = os.path.join(dataset_path, 'cvat1.1.xml')
    dataset_classes = os.path.join(dataset_path, 'classes.txt')

    name_list = os.listdir(dataset_image)   # 获取image文件列表
    with open(dataset_classes, "r", encoding='UTF-8') as f:
        classes = f.read().splitlines()
    classes.append('_background_')

    xml_file = dataset_cvat
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'version').text = '1.1'

    annotation_meta = ET.SubElement(annotation, 'meta')
    annotation_meta_task = ET.SubElement(annotation_meta, 'task')
    ET.SubElement(annotation_meta_task, 'size').text = str(len(name_list))
    ET.SubElement(annotation_meta_task, 'stop_frame').text = str(len(name_list) - 1)

    annotation_meta_task_labels = ET.SubElement(annotation_meta_task, 'labels')
    for label in classes:
        annotation_meta_task_labels_label = ET.SubElement(annotation_meta_task_labels, 'label')
        ET.SubElement(annotation_meta_task_labels_label, 'name').text = label
        ET.SubElement(annotation_meta_task_labels_label, 'color').text = f'#{random.randint(0, 0xFFFFFF):06x}'
        ET.SubElement(annotation_meta_task_labels_label, 'type').text = 'polygon' if label == '_background_' else 'any'

    # 遍历图片生成标签
    total_name = len(name_list)
    for i, name in enumerate(tqdm(name_list, total=total_name)):
        progress = (i + 1) * 100 // total_name
        gen_status["progress"] = progress
        gen_status["status"] = "生成中"

        image_name = name
        label_path = os.path.join(dataset_yolo, name.split('.')[0]+'.txt')
        width_img, height_img = imagesize.get(os.path.join(dataset_image, image_name))
        annotation_image = ET.SubElement(annotation, 'image', {
            'id': str(i),
            'name': image_name,
            'width': str(width_img),
            'height': str(height_img)
        })
        if not os.path.exists(label_path):
            continue

        objects_bbox = []
        with open(label_path, "r", encoding='UTF-8') as f:
            objects_bbox = f.read().splitlines()

        for object_info in objects_bbox:
            object_info = object_info.strip().split(' ')
            x_center = float(object_info[1]) * width_img + 1
            y_center = float(object_info[2]) * height_img + 1
            xminVal = round(x_center - 0.5 * float(object_info[3]) * width_img, 2)
            yminVal = round(y_center - 0.5 * float(object_info[4]) * height_img, 2)
            xmaxVal = round(x_center + 0.5 * float(object_info[3]) * width_img, 2)
            ymaxVal = round(y_center + 0.5 * float(object_info[4]) * height_img, 2)
            class_index = int(float(object_info[0]))
            polygon = [(xminVal, yminVal), (xmaxVal, yminVal), (xmaxVal, ymaxVal), (xminVal, ymaxVal)]
            points = ";".join(f"{x},{y}" for x, y in polygon)
            ET.SubElement(annotation_image, 'polygon', {
                'label': classes[class_index],
                'source': 'manual',
                'points': points,
                'z_order': '0'
            })

    # 使用minidom进行格式化保存
    annotation_str = ET.tostring(annotation, encoding='utf-8')
    dom = minidom.parseString(annotation_str)
    pretty_xml_str = dom.toprettyxml(indent="  ", newl="\n")
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)

    gen_status["progress"] = 100
    gen_status["status"] = "已生成"

    return jsonify({"message": f"执行完成！", "gen_status": gen_status}), 200

# 查询进度
def get_genprogress():
    return  jsonify({"message": f"请求成功！", "gen_status": gen_status}), 200

# 启动生成任务的线程
def start_gen_task(dataset_path):
    # gen_thread = threading.Thread(target=gen_cvat1_1, args=(dataset_path,))
    # gen_thread.start()
    data = gen_cvat1_1(dataset_path)
    return data

if __name__ == "__main__":
    dataset_path = r'E:\vision\yolov8\ultralytics-main\runs\detect\predict10'
    start_gen_task(dataset_path)
    while gen_status["progress"] < 100:
        print(f"当前进度: {get_genprogress()['progress']}%, 状态: {get_genprogress()['status']}")
