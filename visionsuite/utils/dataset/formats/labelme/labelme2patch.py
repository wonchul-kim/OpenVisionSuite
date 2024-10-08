import glob 
import os.path as osp 
import cv2 
import json
import os
from tqdm import tqdm 
import numpy as np
from copy import deepcopy

from visionsuite.utils.dataset.formats.labelme.utils import add_labelme_element, init_labelme_json 

def intersection(boxA, boxB):
    # Box coordinates
    xmin1, ymin1 = boxA[0]
    xmax1, ymax1 = boxA[1]
    xmin2, ymin2 = boxB[0]
    xmax2, ymax2 = boxB[1]
    
    # Calculate the (x, y) coordinates of the intersection rectangle
    inter_xmin = max(xmin1, xmin2)
    inter_ymin = max(ymin1, ymin2)
    inter_xmax = min(xmax1, xmax2)
    inter_ymax = min(ymax1, ymax2)
    
    # Check if there is an intersection
    if inter_xmin < inter_xmax and inter_ymin < inter_ymax:
        return [[inter_xmin, inter_ymin], [inter_xmax, inter_ymax]]
    else:
        # No intersection
        return None


def min_max_normalize(image_array, min_val, max_val):
    normalized_array = (image_array - min_val) / (max_val - min_val)
    return np.clip(normalized_array, 0, 1)  # 값을 0과 1 사이로 클리핑


def labelme2patches(input_dir, output_dir, patch_width, patch_height, 
                    image_ext='bmp', patch_overlap_ratio = 0.2,
                    norm_val=None):

    if not osp.exists(output_dir):
        os.mkdir(output_dir)
    
    dx = int((1. - patch_overlap_ratio) * patch_width)
    dy = int((1. - patch_overlap_ratio) * patch_height)


    img_files = glob.glob(osp.join(input_dir, '*.bmp'))
    for img_file in tqdm(img_files):
        filename = osp.split(osp.splitext(img_file)[0])[-1]
        json_file = osp.splitext(img_file)[0] + '.json'
        with open(json_file, 'r') as jf:
            anns = json.load(jf)['shapes']
        
        img = cv2.imread(img_file)
        img_h, img_w, img_c = img.shape
        
        num_patches = 0
        for y0 in range(0, img_h, dy):
            for x0 in range(0, img_w, dx):
                num_patches += 1
                if y0 + patch_height > img_h:
                    y = img_h - patch_height
                else:
                    y = y0

                if x0 + patch_width > img_w:
                    x = img_w - patch_width
                else:
                    x = x0
        
                _labelme = init_labelme_json(filename + f'_{num_patches}.{image_ext}', img_w, img_h)
                xmin, xmax, ymin, ymax = x, x + patch_width, y, y + patch_height
                window = [[xmin, ymin], [xmax, ymax]]

                included = False
                for ann in anns:
                    points = ann['points']
                    intersected_box = intersection(window, points)
                    
                    if intersected_box:
                        included = True 
                        
                        for intersected_point in intersected_box:
                            intersected_point[0] -= xmin
                            intersected_point[1] -= ymin
                        _labelme = add_labelme_element(_labelme, ann['shape_type'], ann['label'], intersected_box)
                        
                if included:
                    if norm_val is not None:
                        if norm_val['type'] == 'min_max':
                            patch = min_max_normalize(deepcopy(img[ymin:ymax, xmin:xmax, :]), norm_val['min_val'], norm_val['max_val'])
                            patch = (patch * 255).astype(np.uint8)
                    else:
                        patch = deepcopy(img[ymin:ymax, xmin:xmax, :])
                    cv2.imwrite(osp.join(output_dir, filename + f'_{num_patches}.{image_ext}'), 
                                cv2.cvtColor(patch, cv2.COLOR_RGB2BGR))
                    with open(osp.join(output_dir, filename + f'_{num_patches}.json'), 'w') as jf:
                        json.dump(_labelme, jf)


input_dir = '/HDD/datasets/projects/sungjin/body/test'
output_dir = '/HDD/datasets/projects/sungjin/body/test/patches'

patch_overlap_ratio = 0.2
patch_width = 1024
patch_height = 1024

# norm_val = {'type': 'min_max', 'min_val': 44, 'max_val': 235}
norm_val = None
    
labelme2patches(input_dir, output_dir, patch_width, patch_height,
                norm_val=norm_val)
                        
                    
                    
                



                


