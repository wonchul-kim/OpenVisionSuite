from visionsuite.cores.unets.keras_unet_collection.models import unet_3plus_2d

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
deep_supervision=False

backbone=None
weights='imagenet'
freeze_backbone=True
freeze_batch_norm=True
name='unet3plus'
                  
model = unet_3plus_2d(input_size, n_labels, filter_num_down)

from visionsuite.cores.unets.keras_unet_collection import losses

def hybrid_loss(y_true, y_pred):

    loss_focal = losses.focal_tversky(y_true, y_pred, alpha=0.5, gamma=4/3)
    loss_iou = losses.iou_seg(y_true, y_pred)
    
    # (x) 
    #loss_ssim = losses.ms_ssim(y_true, y_pred, max_val=1.0, filter_size=4)
    
    return loss_focal+loss_iou #+loss_ssim

from glob import glob
import numpy as np
from tensorflow import keras
import visionsuite.cores.unets.keras_unet_collection.utils as utils

def input_data_process(input_array):
    '''converting pixel vales to [0, 1]'''
    return input_array/255.

def target_data_process(target_array):
    '''Converting tri-mask of {1, 2, 3} to three categories.'''
    return keras.utils.to_categorical(target_array-1)

input_dir = '/HDD/datasets/projects/22.03.22_flange_s/data'
mask_input_dir = '/HDD/datasets/projects/22.03.22_flange_s/mask'

sample_names = np.array(sorted(glob(input_dir + '/*.bmp')))
label_names = np.array(sorted(glob(mask_input_dir + '/*.bmp')))

L = len(sample_names)
ind_all = utils.shuffle_ind(L)

L_train = int(0.8*L); L_valid = int(0.1*L); L_test = L - L_train - L_valid
ind_train = ind_all[:L_train]; ind_valid = ind_all[L_train:L_train+L_valid]; ind_test = ind_all[L_train+L_valid:]
print("Training:validation:testing = {}:{}:{}".format(L_train, L_valid, L_test))

valid_input = input_data_process(utils.image_to_array(sample_names[ind_test], size=512, channel=3))
valid_target = target_data_process(utils.image_to_array(label_names[ind_test], size=512, channel=1))
# valid_input = input_data_process(utils.image_to_array(sample_names[ind_valid], size=512, channel=3))
# valid_target = target_data_process(utils.image_to_array(label_names[ind_valid], size=512, channel=1))

test_input = input_data_process(utils.image_to_array(sample_names[ind_test], size=512, channel=3))
test_target = target_data_process(utils.image_to_array(label_names[ind_test], size=512, channel=1))

N_epoch = 10 # number of epoches
N_batch = 100 # number of batches per epoch
N_sample = 32 # number of samples per batch

tol = 0 # current early stopping patience
max_tol = 3 # the max-allowed early stopping patience
min_del = 0 # the lowest acceptable loss value reduction 

model.compile(loss=[hybrid_loss, hybrid_loss, hybrid_loss, hybrid_loss, hybrid_loss],
                  loss_weights=[0.25, 0.25, 0.25, 0.25, 1.0],
                  optimizer=keras.optimizers.Adam(learning_rate=1e-4))

# loop over epoches
for epoch in range(N_epoch):
    
    # initial loss record
    if epoch == 0:
        temp_out = model.predict([valid_input])
        y_pred = temp_out[-1]
        record = np.mean(hybrid_loss(valid_target, y_pred))
        print('\tInitial loss = {}'.format(record))
    
    # loop over batches
    for step in range(N_batch):
        # selecting smaples for the current batch
        ind_train_shuffle = utils.shuffle_ind(L_train)[:N_sample]
        
        # batch data formation
        ## augmentation is not applied
        train_input = input_data_process(
            utils.image_to_array(sample_names[ind_train][ind_train_shuffle], size=128, channel=3))
        train_target = target_data_process(
            utils.image_to_array(label_names[ind_train][ind_train_shuffle], size=128, channel=1))
        
        # train on batch
        loss_ = model.train_on_batch([train_input,], 
                                         [train_target, train_target, train_target, train_target, train_target,])
#         if np.isnan(loss_):
#             print("Training blow-up")

        # ** training loss is not stored ** #
        
    # epoch-end validation
    temp_out = model.predict([valid_input])
    y_pred = temp_out[-1]
    record_temp = np.mean(hybrid_loss(valid_target, y_pred))
    # ** validation loss is not stored ** #
    
    # if loss is reduced
    if record - record_temp > min_del:
        print('Validation performance is improved from {} to {}'.format(record, record_temp))
        record = record_temp; # update the loss record
        tol = 0; # refresh early stopping patience
        # ** model checkpoint is not stored ** #

    # if loss not reduced
    else:
        print('Validation performance {} is NOT improved'.format(record_temp))
        tol += 1
        if tol >= max_tol:
            print('Early stopping')
            break;
        else:
            # Pass to the next epoch
            continue;