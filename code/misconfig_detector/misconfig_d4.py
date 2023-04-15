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
        car = items[14]

        if car not in misconfig_dict:
            misconfig_dict[car] = {}
        
        highest_pri = items[-2]
        higher_serv = items[-1]

        if highest_pri == 'True' or higher_serv == 'True':
            cid = items[4]
            freq = items[6]

            cell_str = freq + '-' + cid
            if cell_str not in misconfig_dict[car]:
                misconfig_dict[car][cell_str] = [freq, cid, 0]
            misconfig_dict[car][cell_str][2] += 1
                
p = output_path + "/" + "misconfig_d4.csv"
fout = open(p, 'w')
fout.write('operator,pcell,freq,count\n')
for k1, v1 in misconfig_dict.items():
    for k2, v2 in v1.items():
        line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
        fout.write(line + '\n')
fout.close()
    
