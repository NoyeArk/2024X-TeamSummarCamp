import os
import json
import argparse
from PIL import Image

# 标签对应的索引，如Bicycle-0, Boat-1....
labels = ['Bicycle', 'Boat', 'Bottle', 'Bus', 'Car', 'Cat', 'Chair', 'Cup', 'Dog', 'Motorbike', 'People', 'Table']


# 转化成RGB格式，避免Libpng警告
def fix_image_profile(img):
    try:
        img = img.convert("RGB")
    except Exception as e:
        print(f"Error fixing color profile: {e}")
    return img


# 同一数据集格式-jpg
def convert_to_jpg(img_path, output_path):
    try:
        img = Image.open(img_path)
        img = fix_image_profile(img)
        jpg_path = os.path.splitext(output_path)[0] + ".jpg"
        img.save(jpg_path)
        return jpg_path
    except Exception as e:
        print(f"Error converting {img_path} to JPG: {e}")
        return None


def ExDark2Yolo(txts_dir: str, imgs_dir: str, ratio: str, version: int, output_dir: str):
    ratios = ratio.split(':')
    ratio_train, ratio_test, ratio_val = int(ratios[0]), int(ratios[1]), int(ratios[2])
    ratio_sum = ratio_train + ratio_test + ratio_val
    dataset_perc = {'train': ratio_train / ratio_sum, 'test': ratio_test / ratio_sum, 'val': ratio_val / ratio_sum}

    annotations_data = []
    images_data = []

    for label in labels:
        print(f'Processing {label}...')
        filenames = os.listdir('/'.join([txts_dir, label]))
        cur_idx = 0
        files_num = len(filenames)

        cnt = 1

        for filename in filenames:
            print('filename:', filename)
            cur_idx += 1
            if cur_idx < dataset_perc.get('train') * files_num:
                set_type = 'train'
            elif cur_idx < (dataset_perc.get('train') + dataset_perc.get('test')) * files_num:
                set_type = 'test'
            else:
                set_type = 'val'

            name_split = filename.split('.')
            img_path = '/'.join([imgs_dir, label, '.'.join(filename.split('.')[:-1])])
            img = Image.open(img_path)
            jpg_path = convert_to_jpg(img_path, '/'.join([output_dir, set_type, 'images', os.path.basename(img_path)]))

            width, height = img.size
            txt = open('/'.join([txts_dir, label, filename]), 'r')
            txt.readline()  # ignore first line
            line = txt.readline()

            annotation_data = []

            while line != '':
                datas = line.strip().split()
                class_idx = labels.index(datas[0])
                x0, y0, w0, h0 = int(datas[1]), int(datas[2]), int(datas[3]), int(datas[4])
                bbox = [x0, y0, w0, h0]
                if version == 5:
                    x = (x0 + w0/2) / width
                    y = (y0 + h0/2) / height
                elif version == 3:
                    x = x0 / width
                    y = y0 / height
                else:
                    print("Version of YOLO error.")
                    return
                w = w0 / width
                h = h0 / height

                # 1个图片可以有多个检测目标
                annotations_data.append({
                    'id': cnt,
                    'image_id': int(filename[5:-8]),
                    'bbox': bbox,
                    'category_id': class_idx,
                    'area': w0 * h0,
                    'file_name': filename[5:-4]
                })
                line = txt.readline()

            # 图片的信息只添加1次
            images_data.append({
                'id': int(filename[5:-8]),
                'file_name': filename[:-4],
                'height': height,
                'width': width
            })
            cnt += 1
            # annotations_data.append(annotation_data)

        break

    categories_data = []
    for i in range(len(labels)):
        categories_data.append({
            'id': i,
            'name': labels[i]
        })

    data = {
        'images': images_data,
        'annotations': annotations_data,
        'categories': categories_data
    }
    json_path = '/'.join([output_dir + '.json'])
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--anndir', type=str, default='../ExDark/Annnotations', help="ExDark注释文件夹路径.")
    parser.add_argument('--imgdir', type=str, default='../ExDark/images', help="ExDark图像文件夹路径")
    parser.add_argument('--ratio', type=str, default='8:1:1', help="划分比率 train/test/val, default 8:1:1.")
    parser.add_argument('--version', type=int, choices=[3, 5], default=5, help="转化的YOLO版本，YOLOv3和YOLOv5，YOLOv8的数据集格式跟YOLOv5一致")
    parser.add_argument('--output-dir', type=str, default="../ExDark/processed", help="YOLO格式数据集输出的文件夹路径")
    args = parser.parse_args()
    ExDark2Yolo(args.anndir, args.imgdir, args.ratio, args.version, args.output_dir)
