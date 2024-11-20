"""
将yolo的分割标签转为yolo的目标检测标签
"""
import os
import cv2
import numpy as np
from tqdm import tqdm


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

def process_folder(image_dir, label_dir, output_dir):
    """
    遍历文件夹中的图像和标签文件，并调用转换函数处理每个图像。
    :param image_dir: 包含图像文件的目录
    :param label_dir: 包含标签文件的目录
    :param output_dir: 输出目录
    """
    print("output_dir", output_dir)
    os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在

    image_extensions = ['.png', '.jpg', '.jpeg']  # 图像文件扩展名列表

    for label_filename in tqdm(os.listdir(label_dir)):
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

if __name__ == '__main__':
    # 示例调用
    """
    图像路径
    分割标签路径
    输出矩形标签路径
    """
    image_path = r'D:\10.21_240821Ba\images'
    label_path = r'D:\10.21_240821Ba\labels'
    output_dir = r'D:\10.21_240821Ba\lab'

    process_folder(image_path, label_path, output_dir)
