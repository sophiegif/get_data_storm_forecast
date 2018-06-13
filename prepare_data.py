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

# get 1/4 of the years in testing, 2/4 in training (private), 1/4 in public
years_test=[]
years_train=[]
years_public=[]
for year in range(1979,2018):
    if (year-1979)%4==3:
        years_test.append(year)
    elif (year-1979)%4==1:
        years_public.append(year)
    else:
        years_train.append(year)


data_train=[data for data in data if int(data[0][:4]) in years_train]
data_test=[data for data in data if int(data[0][:4]) in years_test]
data_public=[data for data in data if int(data[0][:4]) in years_public]

data_folders=[data_test,data_train,data_public]
years_group=[years_test,years_train,years_public]
names=['test','train','public']

data_folders=[data_public]
years_group=[years_public]
names=['public']

# loading image data one fold at a time for memory issues
for years,data_f,name in zip(years_group,data_folders,names):
    print(name)
    data_image={}
    with open(file_image, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        columns_image = spamreader.__next__()
        for row in spamreader:
            if row[0] in storms and int(row[0][:4]) in years:
                data_image[(row[0],row[1])]=row[2:]
    print('loading images done.')

    for i in range(len(data_f)):
        if (data_f[i][0],data_f[i][1]) not in data_image.keys():
            data_f[i] = data_f[i] + [0]*size_crop*size_crop
        else:
            data_f[i]=data_f[i]+data_image[(data_f[i][0],data_f[i][1])]
            data_image[(data_f[i][0], data_f[i][1])]=[]

    if name in ['train','test']:
        write_csv('data/' + name + '.csv', columns + columns_image[2:], data_f)
        print('writing data csv done.')
        data_f=[]


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
write_csv('data/public_train.csv', columns+ columns_image[2:],data_public_train)
write_csv('data/public_test.csv', columns+ columns_image[2:],data_public_test)
print('writing public data csv done.')

# copy starting kit files to <ramp_kits_dir>/<ramp_name>/data
#copyfile(
#    os.path.join('data', 'public_train.csv'),
#    os.path.join(ramp_kits_dir, ramp_name, 'data', 'train.csv')
#)
#copyfile(
#    os.path.join('data', 'public_test.csv'),
#    os.path.join(ramp_kits_dir, ramp_name, 'data', 'test.csv')
#)
