import collections
import os
import sys
import math

from stat_analyzer import StatAnalyzer

loc_time_digits = 2

serving_cellset_trace = {}
serving_cell_trace = {}
pcell_trace = {}
cell_trace = {}

def handle_taskround_directory(tagdata, car):
    global serving_cellset_trace, serving_cell_trace, pcell_trace, cell_trace

    if car not in pcell_trace:
        pcell_trace[car] = {}
    if car not in serving_cell_trace:
        serving_cell_trace[car] = {}
    if car not in serving_cellset_trace:
        serving_cellset_trace[car] = {}
    if car not in cell_trace:
        cell_trace[car] = {}

    parser = StatAnalyzer(tagdata)
    serving_cellset_trace_cus_ts = parser.serving_cellset_trace
    serving_cell_trace_cus_ts = parser.serving_cell_trace
    pcell_trace_cus_ts = parser.pcell_trace
    cell_trace_cus_ts = parser.cell_trace

    #print(serving_cellset_trace_cus_ts)
    #print(serving_cell_trace_cus_ts)
    #print(pcell_trace_cus_ts)

    for k, v in serving_cellset_trace_cus_ts.items():
        if k not in serving_cellset_trace[car]:
            serving_cellset_trace[car][k] = 0
        serving_cellset_trace[car][k] += v

    for k, v in serving_cell_trace_cus_ts.items():
        if k not in serving_cell_trace[car]:
            serving_cell_trace[car][k] = [v[0], v[1], 0]
        serving_cell_trace[car][k][2] += v[2]

    for k, v in pcell_trace_cus_ts.items():
        if k not in pcell_trace[car]:
            pcell_trace[car][k] = [v[0], v[1], 0]
        pcell_trace[car][k][2] += v[2]

    for k, v in cell_trace_cus_ts.items():
        if k not in cell_trace[car]:
            cell_trace[car][k] = [v[0], v[1], 0]
        cell_trace[car][k][2] += v[2]

def parse_taskrounds(tagdata_dir):
    for subdir, dirs, files in os.walk(tagdata_dir):
        for name in files:
            if name.find('txt') < 0:
                continue
            print(name)
            tagdata = os.path.join(subdir, name)

            carrier = ''
            if name.find('-a-') >= 0 or name.find('-A-') >= 0 or name.find('-a.') >= 0 or name.find('-A.') >= 0:
                carrier = '310410'
            elif name.find('-v-') >= 0 or name.find('-V-') >= 0 or name.find('-v.') >= 0 or name.find('-V.') >= 0:
                carrier = '311480'
            elif name.find('-t-') >= 0 or name.find('-T-') >= 0 or name.find('-t.') >= 0 or name.find('-T.') >= 0:
                carrier = '310260'
            else:
                continue

            print(carrier)

            handle_taskround_directory(tagdata, carrier)

def printer(outputpath):
    global serving_cellset_trace, serving_cell_trace, pcell_trace, cell_trace

    fout = open(outputpath + '/' + 'serving_cellset_list.csv', 'w')
    fout.write('carrier,serving_cellset,count\n')
    for k1, v1 in serving_cellset_trace.items():
        for k2, v2 in v1.items():
            if len(k2) == 0:
                continue
            line = str(k1) + ',' + str(k2) + ',' + str(v2)
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'serving_cell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in serving_cell_trace.items():
        for k2, v2 in v1.items():
            if k2.find('None') >= 0:
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'cell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in cell_trace.items():
        for k2, v2 in v1.items():
            if k2.find('None') >= 0:
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'pcell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in pcell_trace.items():
        for k2, v2 in v1.items():
            if k2.find('None') >= 0:
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

if __name__ == "__main__":

    parse_taskrounds(sys.argv[1])
    printer(sys.argv[2])
