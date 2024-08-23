from abc import abstractmethod

from albumentations.core.transforms_interface import DualTransform

class CustomAlbumentations(DualTransform):
    def __init__(self):
        self.augmenter = None
        
    @abstractmethod
    def apply(self, img, **params):
        return self.augmenter(img)
    
    @abstractmethod
    def apply_to_mask(self, mask, **params):
        pass 
    
    @abstractmethod
    def apply_to_bbox(self, bbox, **params):
        pass

    @abstractmethod
    def apply_to_keypoint(self, keypoint, **params):
        pass