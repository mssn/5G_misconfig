import collections
import os
import sys
import math

loc_time_digits = 2

dist2 = {}

def merge_data(folder):
    global dist2
    dataset_list = ['indy', 'chicago', 'la', 'wl', 'cn']
    instance_list = ['a1a2', 'b1a2', 'missed_4g', 'missed_5g', 'a3a6', 'd4', 'd5']

    dist2 = {}

    for dataset in dataset_list:

        dist2[dataset] = {}

        op_list = []
        if dataset == 'cn':
            op_list = ['china_mobile']
        else:
            op_list = ['att', 'verizon', 'tmobile']

        for op in op_list:

            dist2[dataset][op] = {}

            for instance in instance_list:
                dist2[dataset][op][instance] = []

    for subdir, dirs, files in os.walk(folder):
        for name in files:
            if name.find('.csv') < 0:
                continue
            print(name)
            file_path = os.path.join(subdir, str(name))
            print(file_path)

            dataset = ''
            case = ''
            case_index = 0
            for k in dataset_list:
                if file_path.find(k) >= 0:
                    dataset = k
            for k in instance_list:
                if file_path.find(k) >= 0:
                    case = k

            with open(file_path, 'r') as lines:
                for line in lines:
                    if 'operator' in line:
                        continue
                    items = line.strip().split(',')
                    car = ''
                    if items[0] == '310410' or items[0] == 'att' or items[0] == 'ATT':
                        car = 'att'
                    elif items[0] == '311480' or items[0] == 'verizon' or items[0] == 'Verizon':
                        car = 'verizon'
                    elif items[0] == '310260' or items[0] == 'tmobile' or items[0] == 'T-Mobile' or items[0] == '310120' or items[0] == '31100' or items[0] == 'sprint' or items[0] == 'Sprint':
                        car = 'tmobile'
                    elif items[0] == '46000' or items[0] == '46001' or items[0] == 'china mobile':
                        car = 'china_mobile'
                    else:
                        continue

                    print(case)
                    print(line)

                    line_new = ''
                    if case == 'd4' or case == 'd5':
                        line_new = str(items[1]) + '-' + items[2] + ','
                        for i in range(3, len(items)):
                            line_new += str(items[i]) + ','
                    else:
                        for i in range(1, len(items)):
                            line_new += str(items[i]) + ','

                    dist2[dataset][car][case].append(line_new)

def printer(outputpath):
    global dist2

    for k1, v1 in dist2.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2.items():
                if len(v3) == 0:
                    continue

                case = k3
                if case == 'a1a2':
                    case = 'd1-a1a2'
                elif case == 'b1a2':
                    case = 'd1-b1a2'
                elif case == 'missed_4g':
                    case = 'd2-missed_4g'
                elif case == 'missed_5g':
                    case = 'd2-missed_5g'
                elif case == 'a3a6':
                    case = 'd3'
                output_file_name = 'misconfig_' + str(case) + '_' + str(k1) + '_' + str(k2) + '.csv'
                fout = open(outputpath + '/' + output_file_name, 'w')
                if k3 == 'a1a2':
                    fout.write('pcell,freq,thres_a1,thres_a2,count\n')
                elif k3 == 'b1a2':
                    fout.write('pcell,freq,thres_b1,thres_a2,count\n')
                elif k3 == 'missed_4g':
                    fout.write('pcell,freq\n')
                elif k3 == 'missed_5g':
                    fout.write('pcell\n')
                elif k3 == 'a3a6':
                    fout.write('pcell,freq,thres_a3,thres_a6,count\n')
                elif k3 == 'd4':
                    fout.write('pcell,count\n')
                elif k3 == 'd5':
                    fout.write('pcell,count\n')
                for line in v3:
                    fout.write(line + '\n')
                fout.close()

if __name__ == "__main__":

    merge_data(sys.argv[1])
    printer(sys.argv[2])
