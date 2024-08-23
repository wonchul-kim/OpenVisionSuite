import random
import imgaug.augmenters as iaa
from .custom_albumentations import CustomAlbumentations

class Salt(CustomAlbumentations):
    def __init__(self, p=0, per_channel=False):
        super(CustomAlbumentations, self).__init__()
        self.augmenter = iaa.Salt(p=p, per_channel=per_channel)

    def apply(self, img, **params):
        return self.augmenter(image=img)

    def apply_to_mask(self, mask, **params):
        return mask
    
    def apply_to_bbox(self, bbox, **params):
        raise bbox

    def apply_to_keypoint(self, keypoint, **params):
        return keypoint
    

class Pepper(CustomAlbumentations):
    def __init__(self, p=0, per_channel=False):
        super(CustomAlbumentations, self).__init__()
        self.augmenter = iaa.Pepper(p=p, per_channel=per_channel)

    def apply(self, img, **params):
        return self.augmenter(image=img)

    def apply_to_mask(self, mask, **params):
        return mask
    
    def apply_to_bbox(self, bbox, **params):
        raise bbox

    def apply_to_keypoint(self, keypoint, **params):
        return keypoint
    

class SaltAndPepper(CustomAlbumentations):
    def __init__(self, p=0, per_channel=False):
        super(CustomAlbumentations, self).__init__()
        self.augmenter = iaa.SaltAndPepper(p=p, per_channel=per_channel)

    def apply(self, img, **params):
        return self.augmenter(image=img)

    def apply_to_mask(self, mask, **params):
        return mask
    
    def apply_to_bbox(self, bbox, **params):
        raise bbox

    def apply_to_keypoint(self, keypoint, **params):
        return keypoint
    
