
from visionsuite.cores.roboflow.configs.train_config_yolov8 import TrainConfig as YoloV8TrainConfig
from visionsuite.cores.roboflow.configs.train_config_yolov10 import TrainConfig as YoloV10TrainConfig

class Agent:
    
    @classmethod
    def get_tasks(cls):
        return ['classification', 'hbb detection', 'obb detection', 'instance segmentation']
    
    @classmethod
    def get_models_by_task(cls, task):
        if task == 'clssification':
            NotImplementedError 
        elif task == 'hbb detection':
            return cls.get_hbb_det_models()
        elif task == 'obb detection':
            return cls.get_obb_det_models()
        elif task == 'instance segmentation':
            return cls.get_seg_models()
        
    @classmethod
    def get_cls_models(cls):
        return ['yolov8']
    
    @classmethod
    def get_hbb_det_models(cls):
        return ['yolov8']
    
    @classmethod
    def get_obb_det_models(cls):
        return ['yolov8', 'yolov10']
    
    @classmethod
    def get_seg_models(cls):
        return ['yolov8']
    
    @staticmethod
    def get_schema_by_model(model):
        if model == 'yolov8':
            return {"TrainConfig": YoloV8TrainConfig.model_json_schema(mode='serialization')}
        elif model == 'yolov10':
            return {"TrainConfig": YoloV10TrainConfig.model_json_schema(mode='serialization')}
    
    @staticmethod
    def get_yolov8_backbones():
        return ['s', 'm', 'l']