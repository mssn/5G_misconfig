import collections
import os
import sys
import math

loc_time_digits = 2

dist = {}

def parse_dataset_stat(stat_folder):
    global dist
    dataset_list = ['indy', 'chicago', 'la', 'wl', 'cn']

    dist = {}

    for dataset in dataset_list:
        folder = stat_folder + '/' + dataset

        dist[dataset] = {}

        op_list = []
        if dataset == 'cn':
            op_list = ['46000']
        else:
            op_list = ['310410', '311480', '310260']

        for op in op_list:
            '''
            pcell_num_list[dataset][op] = 0 # 0
            cell_num_list[dataset][op] = 0 # 1
            lte_cell_num_list[dataset][op] = 0 # 2
            nr_cell_num_list[dataset][op] = 0 # 3
            serving_cell_num_list[dataset][op] = 0 # 4
            lte_serving_cell_num_list[dataset][op] = 0 # 5
            nr_serving_cell_num_list[dataset][op] = 0 # 6
            serving_cellset_num_list[dataset][op] = 0 # 7
            lte_only_serving_cellset_num_list[dataset][op] = 0 # 8
            nr_lte_serving_cellset_num_list[dataset][op] = 0 # 9
            serving_cellset_unique_num_list[dataset][op] = 0 # 10
            lte_only_serving_cellset_unique_num_list[dataset][op] = 0 # 11
            nr_lte_serving_cellset_unique_num_list[dataset][op] = 0 # 12
            '''

            dist[dataset][op] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for subdir, dirs, files in os.walk(folder):
            for name in files:
                if name.find('.csv') < 0:
                    continue
                print(name)
                file_path = os.path.join(subdir, str(name))
                
                if file_path.find('serving_cellset_list.csv') >= 0:
                    with open(file_path, 'r') as lines:
                        for line in lines:
                            if 'carrier' in line:
                                continue
                            items = line.strip().split(',')
                            try:
                                op = items[0]
                                count = int(items[-1])
                                if op in dist[dataset]:
                                    
                                    serving_cellset_str = items[1].strip().split('/')
                                    nr_flag = 0
                                    for cell in serving_cellset_str:
                                        freq = cell.split('-')[0]
                                        cid = cell.split('-')[1]
                                        
                                        if int(freq) > 100000 or int(cid) > 100000:
                                            nr_flag = 1
                                            break

                                    dist[dataset][op][10] += 1
                                    dist[dataset][op][7] += count

                                    if nr_flag:
                                        dist[dataset][op][12] += 1
                                        dist[dataset][op][9] += count
                                    else:
                                        dist[dataset][op][11] += 1
                                        dist[dataset][op][8] += count
                            except:
                                print(line)
                                continue
                elif file_path.find('serving_cell_list.csv') >= 0:
                    with open(file_path, 'r') as lines:
                        for line in lines:
                            if 'carrier' in line:
                                continue
                            items = line.strip().split(',')
                            op = items[0]
                            try:
                                if op in dist[dataset]:

                                    nr_flag = 0
                                    if int(items[1]) > 100000 or int(items[2]) > 100000:
                                        nr_flag = 1

                                    dist[dataset][op][4] += 1

                                    if nr_flag:
                                        dist[dataset][op][6] += 1
                                    else:
                                        dist[dataset][op][5] += 1
                            except:
                                print(line)
                                continue
                elif file_path.find('pcell_list.csv') >= 0:
                    with open(file_path, 'r') as lines:
                        for line in lines:
                            if 'carrier' in line:
                                continue
                            items = line.strip().split(',')
                            op = items[0]
                            try:
                                freq = int(items[1])
                                cid = int(items[2])
                                if op in dist[dataset]:
                                    dist[dataset][op][0] += 1
                            except:
                                print(line)
                                continue
                elif file_path.find('cell_list.csv') >= 0:
                    with open(file_path, 'r') as lines:
                        for line in lines:
                            if 'carrier' in line:
                                continue
                            items = line.strip().split(',')
                            op = items[0]
                            try:
                                if op in dist[dataset]:

                                    nr_flag = 0
                                    if int(items[1]) > 100000 or int(items[2]) > 100000:
                                        nr_flag = 1

                                    dist[dataset][op][1] += 1
                                
                                    if nr_flag:
                                        dist[dataset][op][3] += 1
                                    else:
                                        dist[dataset][op][2] += 1
                            except:
                                print(line)
                                continue

def printer(outputpath):
    global dist

    fout = open(outputpath + '/' + 'dataset_stat.csv', 'w')
    fout.write('dataset,operator,pcell_num,cell_num,lte_cell_num,nr_cell_num,' + \
        'serving_cell_num,lte_serving_cell_num,nr_serving_cell_num,' + \
        'serving_cellset_num,lte_only_serving_cellset_num,nr_lte_serving_cellset_num,' + \
        'serving_cellset_unique_num,lte_only_serving_cellset_unique_num,nr_lte_serving_cellset_unique_num' + \
        '\n')
    for k1, v1 in dist.items():
        for k2, v2 in v1.items():
            car = ''
            if k2 == '310410':
                car = 'att'
            elif k2 == '311480':
                car = 'verizon'
            elif k2 == '310260':
                car = 'tmobile'
            elif k2 == '46000':
                car = 'china mobile'

            line = str(k1) + ',' + str(car)
            for item in v2:
                line += ',' + str(item)
            fout.write(line + '\n')
    fout.close()

if __name__ == "__main__":

    parse_dataset_stat(sys.argv[1])
    printer(sys.argv[2])
