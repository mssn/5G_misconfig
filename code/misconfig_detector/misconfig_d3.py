import collections
import os
import sys
import math
import datetime
from collections import OrderedDict

input_file = sys.argv[1]
output_path = sys.argv[2]

def check_a3a6_misconfig(meas):
    loop_list = {}
    for freq, v in meas.items():
        if 'a3' in v and 'a6' in v:
            thres_list_a3 = v['a3']
            thres_list_a6 = v['a6']
            
            for thres_a3 in thres_list_a3:
                for thres_a6 in thres_list_a6:
                    threshold_a3 = float(thres_a3.strip('_Non'))
                    threshold_a6 = float(thres_a6.strip('_Non'))
                    
                    if threshold_a3 == threshold_a6:
                        if freq not in loop_list:
                            loop_list[freq] = {}
                        threshold_str = str(threshold_a3) + '|' + str(threshold_a6)
                        if threshold_str not in loop_list[freq]:
                            loop_list[freq][threshold_str] = [threshold_a3, threshold_a6, 0]
                        loop_list[freq][threshold_str][2] += 1
    
    return loop_list

a3a6_misconfig_dict = {}
pcell_str = ""
meas = {}

op = None

with open(input_file, 'r', encoding='utf-8-sig') as lines:
    for line in lines:

        if "Carrier" in line:
            items = line.strip().split(' ')
            if len(items) >= 2:
                op = items[1]
            else:
                op = None
            if op not in a3a6_misconfig_dict:
                a3a6_misconfig_dict[op] = {}
        
        if "Frequency" in line:
            a3a6_misconfig_list = check_a3a6_misconfig(meas)
            
            if len(a3a6_misconfig_list) > 0:
                print(a3a6_misconfig_list)
                a3a6_misconfig_dict[op][pcell_str] = a3a6_misconfig_list

            items = line.strip().split(' ')
            pcell_str = items[1]
            meas = {}
            config_list = []
            a3a6_misconfig_list = {}
            
        if "_S" in line:
            items = line.strip().split(': ')
            freq = items[0]
            event = items[1].strip(', thr/ofst')
            thres = items[2].strip(', hetersis')
            
            if freq not in meas:
                meas[freq] = {}
            if event not in meas[freq]:
                meas[freq][event] = []
            meas[freq][event].append(thres)
                
p = output_path + "/" + "misconfig_a3a6.csv"
fout = open(p, 'w')
fout.write('operator,pcell,freq,thres_a3,thres_a6,count\n')
for k1, v1 in a3a6_misconfig_dict.items():
    for k2, v2 in v1.items():
        for k3, v3 in v2.items():
            for k4, v4 in v3.items():
                line = str(k1) + ',' + str(k2) + ',' + str(k3) + ',' + str(v4[0]) + ',' + str(v4[1]) + ',' + str(v4[2])
                fout.write(line + '\n')
fout.close()
    
