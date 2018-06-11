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


def write_csv(name_file,name_cols,list_of_instants):
    csvfile = open(name_file, 'w')
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(name_cols)
    for list in list_of_instants:
        spamwriter.writerow(list)
    return 0

ramp_kits_dir = '../../ramp-kits'
for arg in sys.argv[1:]:
    tokens = arg.split('=')
    if tokens[0] == 'ramp_kits_dir':
        ramp_kits_dir = tokens[1]
    else:
        print('Unknown argument {}'.format(tokens[0]))
        exit(0)
ramp_name = os.path.basename(os.getcwd())

#df = pd.read_csv(os.path.join('data', '1D_data_no0s.csv'), index_col=0)
file=os.path.join('/home/sgiffard/Documents/Codes/get_data_storm_forecast/data', 'all_data.csv')
data=[]
first=True
with open(file, 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        if first:
            columns=row
            first=False
        else:
            data.append(row)

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

write_csv('data/train.csv', columns,data_train)
write_csv('data/test.csv', columns,data_test)

# get some public data (to test locally) - independent from test and from train on the server.
# select randomly some storms, and keep of the time instants of those storms in one of the folds (test or train)
data_public=[data for data in data if int(data[0][:4]) in years_public]
stormids_public=list(set(np.transpose(data_public)[0]))
stormids_public_train, stormids_public_test=train_test_split(stormids_public, test_size=0.2, random_state=57)
data_public_test=[]
data_public_train=[]
for instant in data_public:
    if instant[0] in stormids_public_test:
        data_public_test.append(instant)
    else:
        data_public_train.append(instant)

write_csv('data/public_train.csv', columns,data_public_train)
write_csv('data/public_test.csv', columns,data_public_test)


# copy starting kit files to <ramp_kits_dir>/<ramp_name>/data
copyfile(
    os.path.join('data', 'public_train.csv'),
    os.path.join(ramp_kits_dir, ramp_name, 'data', 'train.csv')
)
copyfile(
    os.path.join('data', 'public_test.csv'),
    os.path.join(ramp_kits_dir, ramp_name, 'data', 'test.csv')
)
