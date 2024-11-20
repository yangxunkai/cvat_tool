"""
Cvat转yolo分割，ID为classes的顺序
"""
import os
import time
import argparse
import xml.etree.ElementTree as ET

from tqdm import tqdm

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

def cvat_xml_2_txt(parse_xml_file, save_path):
    tree = ET.parse(parse_xml_file)
    root = tree.getroot()

    # 查找每个图像及其对应的掩码
    for image in tqdm(root.findall('.//image')):
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


if __name__ == '__main__':

    deal_dir = r"E:\datasets\toushe\20240830cvat\cvat\job_821_dataset_2024_08_29_08_27_36_cvat for images 1.1"

    for item_dir in os.listdir(deal_dir):
        #print("item_dir", item_dir)

        save_path =  os.path.join(deal_dir, item_dir)
        parse_xml_file = os.path.join(deal_dir, item_dir, "annotations.xml")

        if os.path.isdir(save_path):
            print("save_path", save_path)

            parser = argparse.ArgumentParser()
            parser.add_argument("--parse_xml_file", type=str, default = parse_xml_file,
                                help="This should be a CVAT-exported XML file, with segmentation areas in polygon format.")
            parser.add_argument("--save_path", type=str, default=save_path + "/sgelabels/")
            args = parser.parse_args()

            cvat_xml_2_txt(args)


