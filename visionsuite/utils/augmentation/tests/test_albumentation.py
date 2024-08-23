

import albumentations as A
import cv2 

# # salt --------------------------------------------------------------------------------------
# from visionsuite.utils.augmentation.albumentation import Salt

# p = 1
# per_channel = False    
# img = cv2.imread('/HDD/etc/images/28_1011220321082612_22_right_bottom_03.bmp')
# print(img.shape)

# transform = A.Compose([
#     Salt(p=p, per_channel=per_channel)
# ])
# sample = transform(image=img, mask=img)
# cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_image.bmp", sample['image'])
# cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_mask.bmp", sample['mask'])


# # pepper --------------------------------------------------------------------------------------
# from visionsuite.utils.augmentation.albumentation import Pepper

# p = 1
# per_channel = False    
# img = cv2.imread('/HDD/etc/images/28_1011220321082612_22_right_bottom_03.bmp')
# print(img.shape)

# transform = A.Compose([
#     Pepper(p=p, per_channel=per_channel)
# ])
# sample = transform(image=img, mask=img)
# cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_image.bmp", sample['image'])
# cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_mask.bmp", sample['mask'])

# salt and pepper --------------------------------------------------------------------------------------
from visionsuite.utils.augmentation.albumentation import SaltAndPepper

p = 0.4
per_channel = False    
img = cv2.imread('/HDD/etc/images/28_1011220321082612_22_right_bottom_03.bmp')
print(img.shape)

transform = A.Compose([
    SaltAndPepper(p=p, per_channel=per_channel)
])
sample = transform(image=img, mask=img)
cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_image.bmp", sample['image'])
cv2.imwrite("/HDD/etc/images/28_1011220321082612_22_right_bottom_03_mask.bmp", sample['mask'])
