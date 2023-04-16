import collections
import os
import sys
import math

loc_time_digits = 2

dist = {}

def parse_dataset_stat(folder):
    global dist
    dataset_list = ['indy', 'chicago', 'la', 'wl', 'cn']
    instance_list = ['d1/a1a2', 'd1/b1a2', 'd2/missed_4g', 'd2/missed_5g', 'd3', 'd4', 'd5']

    dist = {}
    dist2 = {}

    for dataset in dataset_list:

        dist[dataset] = {}
        dist2[dataset] = {}

        op_list = []
        if dataset == 'cn':
            op_list = ['china mobile']
        else:
            op_list = ['att', 'verizon', 'tmobile']

        for op in op_list:

            dist[dataset][op] = [0, 0, 0, 0, 0, 0, 0]
            dist2[dataset][op] = {}

            for instance in instance_list:
                dist2[dataset][op][instance] = {}

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

                    if case == 'd1/a1a2':
                        case_index = 0
                    elif case == 'd1/b1a2':
                        case_index = 1
                    elif case == 'd2/missed_4g':
                        case_index = 2
                    elif case == 'd2/missed_5g':
                        case_index = 3
                    elif case == 'd3':
                        case_index = 4
                    elif case == 'd4':
                        case_index = 5
                    elif case == 'd5':
                        case_index = 6

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
                    elif items[0] == '310260' or items[0] == 'tmobile' or items[0] == 'T-Mobile':
                        car = 'tmobile'
                    elif items[0] == '46000' or items[0] == '46001' or items[0] == 'china mobile':
                        car = 'china mobile'
                    else:
                        continue
                    
                    pcell = ''
                    if case == 'd4' or case == 'd5':
                        pcell = items[1] + '-' + items[2]
                    else:
                        pcell = items[1]

                    print(case)
                    print(line)
                    if pcell not in dist2[dataset][car][case]:
                        dist2[dataset][car][case][pcell] = 1
                        dist[dataset][car][case_index] += 1

def printer(outputpath):
    global dist

    fout = open(outputpath + '/' + 'misconfig_stat.csv', 'w')
    fout.write('dataset,operator,d1_a1a2,d1_b1a2,d2_missed_4g,d2_missed_5g,d3,d4,d5\n')
    for k1, v1 in dist.items():
        for k2, v2 in v1.items():
            car = k2

            line = str(k1) + ',' + str(car)
            for item in v2:
                line += ',' + str(item)
            fout.write(line + '\n')
    fout.close()

if __name__ == "__main__":

    parse_dataset_stat(sys.argv[1])
    printer(sys.argv[2])
