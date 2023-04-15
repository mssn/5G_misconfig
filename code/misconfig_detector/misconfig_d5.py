import collections
import os
import sys
import math
import datetime
from collections import OrderedDict

input_file = sys.argv[1]
output_path = sys.argv[2]

misconfig_dict = {}
pcell_str = ""
meas = {}

with open(input_file, 'r', encoding='utf-8-sig') as lines:
    for line in lines:
        
        if "ts" in line:
            continue
        items = line.strip().split(' ')
        car = items[2]

        if car.startswith('3') or car.startswith('e'):
            continue

        if car not in misconfig_dict:
            misconfig_dict[car] = {}
        
        missing_flag = items[-1]

        if missing_flag == 'True':
            cid = items[4]
            freq = items[3]

            cell_str = freq + '-' + cid
            if cell_str not in misconfig_dict[car]:
                misconfig_dict[car][cell_str] = [freq, cid, 0]
            misconfig_dict[car][cell_str][2] += 1
                
p = output_path + "/" + "misconfig_d5.csv"
fout = open(p, 'w')
fout.write('operator,freq,cid,count\n')
for k1, v1 in misconfig_dict.items():
    for k2, v2 in v1.items():
        line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
        fout.write(line + '\n')
fout.close()
    
