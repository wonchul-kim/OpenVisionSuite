# from keras_unet_collection.models import unet_3plus_2d
from keras_unet_collection.models import unet_3plus_2d
from tqdm import tqdm
input_size = (512, 512, 3)
n_labels = 4
filter_num_down = [32, 64, 128, 256, 512]
# filter_num_skip = [32, 32, 32, 32]
# filter_num_aggregate = 160
filter_num_skip='auto'
filter_num_aggregate='auto'

stack_num_down=2
stack_num_up=1
activation='ReLU'
output_activation='Sigmoid',
batch_norm=False
pool=True
unpool=True
deep_supervision=True
loss_weights = [0.25, 0.25, 0.25, 0.25, 1.0]

backbone=None
weights='imagenet'
freeze_backbone=True
freeze_batch_norm=True
name='unet3plus'
                  
model = unet_3plus_2d(input_size, n_labels, filter_num_down, 
                      filter_num_skip=filter_num_skip, filter_num_aggregate=filter_num_aggregate, 
                  stack_num_down=stack_num_down, stack_num_up=stack_num_up, activation=activation,
                  batch_norm=batch_norm, pool=pool, unpool=unpool, deep_supervision=deep_supervision, 
                  backbone=backbone, weights=weights, freeze_backbone=freeze_backbone, freeze_batch_norm=freeze_batch_norm, 
                  name='unet3plus')

from keras_unet_collection import losses

def hybrid_loss(y_true, y_pred):
    loss_focal = losses.focal_tversky(y_true, y_pred, alpha=0.5, gamma=4/3)
    loss_iou = losses.iou_seg(y_true, y_pred)
    
    # (x) 
    #loss_ssim = losses.ms_ssim(y_true, y_pred, max_val=1.0, filter_size=4)
    
    return loss_focal+loss_iou #+loss_ssim

from glob import glob
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"  

import tensorflow as tf 
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # 메모리 증가 허용
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(f"{len(gpus)} Physical GPUs, {len(logical_gpus)} Logical GPUs")
    except RuntimeError as e:
        print(e)
from tensorflow import keras
import keras_unet_collection.utils as utils

def input_data_process(input_array):
    '''converting pixel vales to [0, 1]'''
    return input_array/255.

def target_data_process(target, num_classes):
    # '''Converting tri-mask of {1, 2, 3} to three categories.'''
    # return keras.utils.to_categorical(target_array)

    # (bs, h, w, 1) -> (bs, h, w), squeeze를 통해 채널 차원 제거
    target = np.squeeze(target, axis=-1)
    
    # (bs, h, w) -> (bs, h, w, num_classes)으로 one-hot 인코딩
    target_one_hot = keras.utils.to_categorical(target, num_classes=num_classes)
    
    return target_one_hot

input_dir = '/HDD/_projects/benchmark/semantic_segmentation/new_model/datasets/patches'
mask_input_dir = '/HDD/_projects/benchmark/semantic_segmentation/new_model/datasets/masks'
output_dir = '/HDD/_projects/benchmark/semantic_segmentation/new_model/outputs/unet3p'

import os.path as osp

if not osp.exists(output_dir):
    os.mkdir(output_dir)

sample_names = np.array(sorted(glob(input_dir + '/*.bmp')))
label_names = np.array(sorted(glob(mask_input_dir + '/*.bmp')))

L = len(sample_names)
ind_all = utils.shuffle_ind(L)

L_train = int(0.8*L)
L_valid = int(0.1*L)
L_test = int(0.1*L)
ind_train = ind_all[:L_train]
ind_valid = ind_all[L_train:L_train+L_valid]
ind_test = ind_all[L_train+L_valid:]
print("Training:validation:testing = {}:{}:{}".format(L_train, L_valid, L_test))

valid_input = input_data_process(utils.image_to_array(sample_names[ind_valid], size=512, channel=3))
valid_target = target_data_process(utils.image_to_array(label_names[ind_valid], size=512, channel=1), n_labels)

# test_input = input_data_process(utils.image_to_array(sample_names[ind_test], size=512, channel=3))
# test_target = target_data_process(utils.image_to_array(label_names[ind_test], size=512, channel=1))

N_epoch = 30 # number of epoches
N_sample = 2 # number of samples per batch

tol = 0 # current early stopping patience
max_tol = 3 # the max-allowed early stopping patience
min_del = 0 # the lowest acceptable loss value reduction 

vis_val = True
cnt = 0

# 옵티마이저 정의
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)

# 손실 함수 정의 (여기서는 hybrid_loss를 사용한다고 가정)
def compute_loss(y_true, y_pred):
    # 필요한 손실 계산 수행
    return hybrid_loss(y_true, y_pred)

# 훈련 루프
for epoch in range(N_epoch):
    
    if epoch != 0 and epoch % 9 == 0:
        model.save(osp.join(output_dir, f'/unet3p_{epoch}.h5'))

    train_loss = []
    for step in range(int(L_train/N_sample)):
        print(f"\r train {str(epoch)} ({step}/{int(L_train/N_sample)}) > {str(train_loss[-1]) if len(train_loss) != 0 else ''}", end="")
        
        # 데이터 준비
        ind_train_shuffle = utils.shuffle_ind(L_train)[:N_sample]
        train_input = input_data_process(
            utils.image_to_array(sample_names[ind_train][ind_train_shuffle], size=512, channel=3))
        train_target = target_data_process(
            utils.image_to_array(label_names[ind_train][ind_train_shuffle], size=512, channel=1), n_labels)
        
        with tf.GradientTape() as tape:
            y_pred = model([train_input], training=True)
            if deep_supervision:
                loss = sum([compute_loss(train_target, y_pred[i]) * loss_weight 
                        for i, loss_weight in enumerate(loss_weights)])
            else:
                loss = compute_loss(train_target, y_pred)

        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        train_loss.append(loss.numpy())
        
        if np.isnan(train_loss[-1]):
            print("Training blow-up")
            raise Exception

    print('train loss: ', np.mean(train_loss))

    if epoch != 0 and epoch % 3 == 0:
        val_loss = []
        for step in range(int(L_valid/N_sample)):
            print(f"\r val {str(epoch)} ({step}/{int(L_train/N_sample)}) > {str(train_loss[-1]) if len(train_loss) != 0 else ''}", end="")

            valid_batch = valid_input[N_sample*step:N_sample*(step + 1)]
            y_pred = model([valid_batch], training=False)
            if vis_val:
                import numpy as np
                import imgviz 
                import cv2
                
                vis_dir = osp.join(output_dir, 'vis')
                if not osp.exists(vis_dir):
                    os.mkdir(vis_dir)
                
                for batch_idx in range(len(valid_batch)):
                    
                    vis_img = np.zeros((512, 512*2, 3))
                    vis_img[:, :512, :] = valid_input[N_sample*step:N_sample*(step + 1)][batch_idx]
                    color_map = imgviz.label_colormap(50)
                    mask = np.argmax(y_pred[-1][batch_idx], axis=-1).astype(np.uint8)
                    mask = color_map[mask].astype(np.uint8)
                    vis_img[:, 512:, :] = mask 
                    
                    cv2.imwrite(osp.join(vis_dir, f'{epoch}_{cnt}.bmp'), vis_img)
                    cnt += 1
                    
            if deep_supervision:
                loss = sum([compute_loss(valid_target, y_pred[i]) * loss_weight 
                            for i, loss_weight in enumerate([0.25, 0.25, 0.25, 0.25, 1.0])])
            else:
                loss = compute_loss(valid_target, y_pred)
            val_loss.append(loss.numpy())

        val_loss = np.mean(val_loss)
        print('val loss: ', val_loss)
        model.save(osp.join(output_dir, f'unet3p_{epoch}__.h5'))
