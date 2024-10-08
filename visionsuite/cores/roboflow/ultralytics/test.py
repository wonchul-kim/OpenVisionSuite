import os.path as osp
import os

from src.test_obb import test_obb

if __name__ == '__main__':
    
    model_name = 'yolov10'
    backbone = 'l'
    weights_file = f"/HDD/_projects/benchmark/obb_detection/rich/outputs/{model_name}_obb/train/weights/best.pt"

    input_dir = '/HDD/_projects/benchmark/obb_detection/rich/datasets/split_dataset_box/val'
    json_dir = '/HDD/_projects/benchmark/obb_detection/rich/datasets/split_dataset_box/val'
    output_dir = f'/HDD/_projects/benchmark/obb_detection/rich/tests/{model_name}_{backbone}'
    
    if not osp.exists(output_dir):
        os.mkdir(output_dir)
    
    compare_gt = True
    iou_threshold = 0.7
    conf_threshold = 0.25
    line_width = 3
    font_scale = 2
    imgsz = 768
    _classes = ['BOX']
    input_img_ext = 'bmp'
    output_img_ext = 'jpg'
    output_img_size_ratio = 1

    test_obb(weights_file, imgsz, _classes, input_dir, output_dir, json_dir, compare_gt, 
                iou_threshold, conf_threshold, line_width, font_scale, 
                input_img_ext=input_img_ext, output_img_ext=output_img_ext, output_img_size_ratio=output_img_size_ratio)