import os
import os.path as osp
import json 
import glob 
from shutil import copyfile

input_dir = '/HDD/etc/tenneco'
output_dir = '/HDD/etc/tenneco_pressed'

if not osp.exists(output_dir):
    os.mkdir(output_dir)

json_files = glob.glob(osp.join(input_dir, '*.json'))

for json_file in json_files:
    filename = osp.split(osp.splitext(json_file)[0])[-1]
    
    with open(json_file) as f_json:
        anns = json.load(f_json)['shapes']
        
    for ann in anns:
        label = ann['label']
        
        if label.lower() == 'pressed':
            copyfile(json_file, osp.join(output_dir, filename + '.json'))
            break
            
            
        