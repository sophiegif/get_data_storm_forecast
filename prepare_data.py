"""Script called when preparing a RAMP, either locally or on the backend.

Typically, it creates data/public_train.csv and data/public_test.csv
which will be committed into the repo and used by the starting kit,
and data/train.csv and data/test.csv which are kept locally.

It may also copy data/public_train.csv and data/public_test.csv
into the starting kit data/train.csv and data/test.csv.
"""
import os
import sys
import csv
import pandas as pd
from shutil import copyfile
from sklearn.model_selection import train_test_split
import numpy as np

def write_csv(name_file,name_cols,list_of_instants):
    csvfile = open(name_file, 'w')
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(name_cols)
    for list in list_of_instants:
        spamwriter.writerow(list)
    return 0

#ramp_kits_dir = '../../ramp-kits'
ramp_kits_dir='../ramp_kit_storm_forecast'
for arg in sys.argv[1:]:
    tokens = arg.split('=')
    if tokens[0] == 'ramp_kits_dir':
        ramp_kits_dir = tokens[1]
    else:
        print('Unknown argument {}'.format(tokens[0]))
        exit(0)
ramp_name = os.path.basename(os.getcwd())

# read 0-d data
file=os.path.join('/home/sgiffard/Documents/Codes/get_data_storm_forecast/data', 'all_data.csv')
data=[]
with open(file, 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    columns = spamreader.__next__()
    for row in spamreader:
        data.append(row)
storms=list(set(np.transpose(data)[0])) # names of storms present in ´data´

# read image data - and stack it at the same time
size_crop=25
file_image=os.path.join('/home/sgiffard/Documents/Codes/get_data_storm_forecast/data', 'data_image_pressure_lev700.csv')

test_split=0.25
public_split=0.25
randomseed=47
# split train-test
num_storm = len(storms)
indices = list(range(num_storm))
num_test = int(np.floor(test_split * num_storm))
num_public = int(np.floor(public_split * num_storm))
np.random.seed(randomseed)
np.random.shuffle(indices)

train_idx, public_idx, test_idx = indices[:-num_public - num_test], \
                                 indices[-num_public - num_test:-num_test], indices[-num_test:]

list_idstorms_train = [storms[i] for i in train_idx]
list_idstorms_public = [storms[i] for i in public_idx]
list_idstorms_test = [storms[i] for i in test_idx]

data_train=[d for d in data if d[0] in list_idstorms_train]
data_test=[d for d in data if d[0] in list_idstorms_test]
data_public=[d for d in data if d[0] in list_idstorms_public]
data=[]

data_folders=[data_test,data_train,data_public]
list_idsstorms=[list_idstorms_test,list_idstorms_train ,list_idstorms_public ]
names=['test','train','public']

# data_folders=[data_test]
# list_idsstorms=[list_idstorms_test]
# names=['test']

# loading image data one fold at a time for memory issues
for data_f,name,list_id in zip(data_folders,names, list_idsstorms):
    print(name)
    data_image={}
    with open(file_image, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        columns_image = spamreader.__next__()
        for row in spamreader:
            if row[0] in list_id:
                data_image[(row[0],row[1])]=row[2:]
    print('loading images done.')

    for i in range(len(data_f)):
        if (data_f[i][0],data_f[i][1]) not in data_image.keys():
            data_f[i] = data_f[i] + [0]*size_crop*size_crop
        else:
            data_f[i]=data_f[i]+data_image[(data_f[i][0],data_f[i][1])]
            data_image[(data_f[i][0], data_f[i][1])]=[]


    write_csv('data/' + name + '.csv', columns + columns_image[2:], data_f)
    print('writing data csv done.')
    if name in ['train', 'test']:
        data_f=[]

data_test=[]
data_train=[]

#Data = pd.read_csv('/home/sgiffard/Documents/Codes/get_data_storm_forecast/data/public.csv')
#data_public=np.array(Data)

print('Separating public train and test...')
# get some public data (to test locally) - independent from test and from train on the server.
# select randomly some storms, and keep all the time instants of these storms in one of the folds (test or train)
stormids_public=list(set(np.transpose(data_public)[0]))
stormids_public_train, stormids_public_test=train_test_split(stormids_public, test_size=0.2, random_state=57)
data_public_test=[]
data_public_train=[]

for instant in data_public:
    if instant[0] in stormids_public_test:
        data_public_test.append(instant)
    else:
        data_public_train.append(instant)
    instant=[]

data_public=[]
write_csv('data/public_train.csv', columns+ columns_image[2:],data_public_train)
write_csv('data/public_test.csv', columns+ columns_image[2:],data_public_test)
print('writing public data csv done.')

#copy starting kit files to <ramp_kits_dir>/<ramp_name>/data
copyfile(
   os.path.join('data', 'public_train.csv'),
   os.path.join(ramp_kits_dir, ramp_name, 'data', 'train.csv')
)
copyfile(
   os.path.join('data', 'public_test.csv'),
   os.path.join(ramp_kits_dir, ramp_name, 'data', 'test.csv')
)
