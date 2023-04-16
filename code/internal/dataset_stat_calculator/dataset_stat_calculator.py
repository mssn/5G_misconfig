import os
from collections import defaultdict
import re
import operator
import sys

pcell_list = {}
serving_cell_list = {}
serving_cellset_list = {}
cell_list = {}

def logNameFromLine(l):
    return l.replace('###', '').replace('[new log] ', '').replace('end', '').strip()

def deviceFromLogName(logName):
    return logName.split('/')[-1].split('_')[4].strip()

def carrierFromLogName(logName):
    return logName.split('/')[-1].replace('.mi3log', '').split('_')[-1].strip()

def getDevCar(l):
    logName = logNameFromLine(l)
    device = deviceFromLogName(logName)
    carrier = carrierFromLogName(logName)
    return '_'.join([device, carrier])

def fileName2dtHms(filename):
    find = re.compile(r'diag_log_[0-9]{8}_[0-9]{6}_')
    result = find.search(filename)
    # time_cmp = result[0].replace('diag_log_', '').strip('_')
    time_cmp = result.group().replace('diag_log_', '').strip('_')
    dt_hms = int(time_cmp.split('_')[0]) * 1000000 + int(time_cmp.split('_')[1])
    return dt_hms

def sortByTime(inputFile):
    f = open(inputFile, 'r')
    lines = f.readlines()
    log_flag, current_dev_car = False, ''
    dev_car_dict_time_list = defaultdict(list) # {dev_car: [time1, time2, ...]}
    dev_car_time_dict_path = {}
    '''
    Extract log information including device, carrier and time
    '''
    for l in lines:
        if '###[new log]' in l:
            current_dev_car = getDevCar(l)
            log_flag = True
        elif '###end' in l and log_flag:
            try:
                this_dev_car = getDevCar(l)
                logName = logNameFromLine(l)
                if this_dev_car == current_dev_car:
                    log_dt_hms = fileName2dtHms(logName)
                    dev_car_dict_time_list[this_dev_car].append(log_dt_hms)
                    dev_car_time_dict_path[this_dev_car + str(log_dt_hms)] = logName
                else:
                    # print('\t'.join([current_dev_car, this_dev_car, 'Wrong order']))
                    pass
            except:
                pass
            log_flag, current_dev_car = False, ''
    '''
    Sort logs of each device_carrier pair by time
    '''
    dev_car_dict_path_list = defaultdict(list)
    for k, time_list in dev_car_dict_time_list.items():
        for t in sorted(time_list):
            dev_car_dict_path_list[k].append(dev_car_time_dict_path[k + str(t)])
    return dev_car_dict_path_list

def segLog(tfile):
    f = open(tfile, 'r')
    lines = f.readlines()
    segDict = defaultdict(str)
    in_log_flag = False
    current_log = ''
    for l in lines:
        if '###[new log]' in l:
            in_log_flag = True
            current_log = l.replace('###', '').replace('[new log] ', '').strip()
            # print(current_log)
        elif '###end' in l and in_log_flag:
            segDict[current_log] += l
            in_log_flag = False
            current_log = ''
        if in_log_flag and current_log:
            segDict[current_log] += l
    return segDict          

def getFreq(logline, keyword, no_cid = False):
    if keyword == 'rrcreq':
        if no_cid:
            return logline.split(' ')[4].split('-')[0]
        else:
            cell_str = logline.split(' ')[4]
            cid = cell_str.split('-')[1]
            freq = cell_str.split('-')[0]
            return [freq, cid]
    if keyword == 'rrcreest':
        if no_cid:
            return logline.split(' ')[5].split('-')[0]
        else:
            cell_str = logline.split(' ')[5]
            cid = cell_str.split('-')[1]
            freq = cell_str.split('-')[0]
            return [freq, cid]
    if keyword == 'handoff':
        cid_freq = logline.split(' ')[-1]
        cid = cid_freq.split('(')[0]
        freq = cid_freq.split(',')[-1].replace(')', '')
        if no_cid:
            return [freq]
        else:
            return [freq, cid]

def checkPcellChange(logline, next_lines):
    pcell = None
    ptn = r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+ Measurement report [0-9]{1} a[3,4,5]{1} .*' #e.g., 2019-05-15 19:54:55.032182 Measurement report 1 a3
    result = re.compile(ptn).match(logline)
    if result:
        for n in next_lines:
            if ' Handoff to ' in n:
                pcell = getFreq(n, 'handoff')
                break
    if ' RRCREQ ' in logline:
        pcell = getFreq(logline, 'rrcreq')
        # print(freq)
    elif ' RRCREEST ' in logline and 'LOG' not in logline:
        pcell = getFreq(logline, 'rrcreest')
        # print(freq)
    elif ' Handoff to ' in logline:
        pcell = getFreq(logline, 'handoff')
    if pcell and int(pcell[0]) < 100:
        print(logline)
        print(pcell)
    return pcell

def parseObj(logline):
    freq = logline.split(' ')[2]
    cell = logline.split(' ')[4]
    if cell == 'None':
        return freq + '_' + 'P'
    else:
        return freq + '_' + 'S'

def parseRpt(logline, nextline, type_only = False):
    htss = logline.split(' ')[2]
    ttt = logline.split(' ')[3]
    tp = nextline.split(' ')[0]
    ofst = nextline.split(' ')[1] + '_' + nextline.split(' ')[2]
    if not type_only: 
        return 'type: ' + tp + ', thr/ofst: ' + ofst + \
            ', hetersis: ' + htss + ', time_to_trigger: ' + ttt
    else:
        return 'type: ' + tp

def mapObjRpt(freq_id_dict, report_dict, logline):
    ids = logline.split('(')[-1]
    freq_id = ids.split(',')[0].strip('\' ')
    rpt_id = ids.split(',')[-1].strip('\') ')
    try:
        return report_dict[rpt_id].replace('type', freq_id_dict[freq_id])
    except:
        return None

def extractConfig(segDict, dev_car_seq, no_filter = True):

    global pcell_list, serving_cell_list, serving_cellset_list

    pcell_list = {}
    serving_cell_list = {}
    serving_cellset_list = {}

    for dev_car, loglist in dev_car_seq.items():
        # print(dev_car)
        car = dev_car.split('_')[-1]
        if car not in pcell_list:
            pcell_list[car] = {}
        if car not in serving_cell_list:
            serving_cell_list[car] = {}
        if car not in serving_cellset_list:
            serving_cellset_list[car] = {}
        if car not in cell_list:
            cell_list[car] = {}
        measstate = set()
        pcell = None
        scell_list = []
        serving_cellset = []
        freq_id_dict = {} # e.g., {'1': '9820_P', '2': '2175_S'}
        report_dict = {} # e.g., {'1': 'type: a1, thr/ofst: 3.0 None, hetersis: 1.0, tt_trigger: 80'}
        obj_flag, rpt_flag, map_flag = False, False, False
        one_meas_state = set()
        for l in loglist:
            logcontent = segDict[l]
            logcontent = logcontent.split('\n')
            for i in range(0, len(logcontent)):
                logline = logcontent[i]
                next_lines = logcontent[i: i + 20]
                #print(logline)
                if checkPcellChange(logline, next_lines):
                    pcell = checkPcellChange(logline, next_lines)
                    cell_str = pcell[0] + '-' + pcell[1]
                    if cell_str not in serving_cell_list[car]:
                        serving_cell_list[car][cell_str] = [pcell[0], pcell[1], 0]
                    serving_cell_list[car][cell_str][2] += 1
                    if cell_str not in pcell_list[car]:
                        pcell_list[car][cell_str] = [pcell[0], pcell[1], 0]
                    pcell_list[car][cell_str][2] += 1
                    if cell_str not in cell_list[car]:
                        cell_list[car][cell_str] = [pcell[0], pcell[1], 0]
                    cell_list[car][cell_str][2] += 1

                    serving_cellset = [[pcell[0], pcell[1]]]
                    serving_cellset_str = pcell[0] + '-' + pcell[1]
                    for item in scell_list:
                        scell_cid = item[1]
                        scell_freq = item[0]
                        serving_cellset.append([scell_freq, scell_cid])
                        serving_cellset_str += '/' + scell_freq + '-' + scell_cid

                    if serving_cellset_str not in serving_cellset_list[car]:
                        serving_cellset_list[car][serving_cellset_str] = [serving_cellset, 0]
                    serving_cellset_list[car][serving_cellset_str][1] += 1

                if not pcell or len(pcell) < 2:
                    continue
                if 'Updated {' in logline:
                    scell_list = []
                    raw_scell_list = logline.strip('Updated {').strip('}').split('), ')
                    serving_cellset = [[pcell[0], pcell[1]]]
                    serving_cellset_str = pcell[0] + '-' + pcell[1]
                    if '{}' not in logline:
                        for item in raw_scell_list:
                            #print(item)
                            raw_scell_str = (item.split(': (')[1]).strip(')')
                            raw_scell_str = raw_scell_str.split(', ')
                            scell_cid = raw_scell_str[0]
                            scell_freq = raw_scell_str[1]
                            scell_list.append([scell_freq, scell_cid])
                            serving_cellset.append([scell_freq, scell_cid])
                            serving_cellset_str += '/' + scell_freq + '-' + scell_cid

                            cell_str = scell_freq + '-' + scell_cid
                            if cell_str not in serving_cell_list[car]:
                                serving_cell_list[car][cell_str] = [scell_freq, scell_cid, 0]
                            serving_cell_list[car][cell_str][2] += 1
                            if cell_str not in cell_list[car]:
                                cell_list[car][cell_str] = [scell_freq, scell_cid, 0]
                            cell_list[car][cell_str][2] += 1

                    if serving_cellset_str not in serving_cellset_list[car]:
                        serving_cellset_list[car][serving_cellset_str] = [serving_cellset, 0]
                    serving_cellset_list[car][serving_cellset_str][1] += 1

                if 'Measurement report' in logline and ('a2' in logline or 'a1' in logline):
                    items = logline.strip().split( )
                    cid = ''
                    if 'Scell' in logline:
                        cid = items[10]
                    else:
                        cid = items[6]
                    freq = items[-1]
                    cell_str = freq + '-' + cid
                    if cell_str not in cell_list[car]:
                        cell_list[car][cell_str] = [freq, cid, 0]
                    cell_list[car][cell_str][2] += 1

def printer(outputpath):
    fout = open(outputpath + '/' + 'serving_cellset_list.csv', 'w')
    fout.write('carrier,serving_cellset,count\n')
    for k1, v1 in serving_cellset_list.items():
        for k2, v2 in v1.items():
            if k1 == '46001' or k1 == '' or k1 == '46011' or k1 == '46605':
                continue
            line = str(k1) + ',' + str(k2) + ',' + str(v2[1])
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'cell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in cell_list.items():
        for k2, v2 in v1.items():
            if k1 == '46001' or k1 == '' or k1 == '46011' or k1 == '46605':
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'serving_cell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in serving_cell_list.items():
        for k2, v2 in v1.items():
            if k1 == '46001' or k1 == '' or k1 == '46011' or k1 == '46605':
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

    fout = open(outputpath + '/' + 'pcell_list.csv', 'w')
    fout.write('carrier,freq,cid,count\n')
    for k1, v1 in pcell_list.items():
        for k2, v2 in v1.items():
            if k1 == '46001' or k1 == '' or k1 == '46011' or k1 == '46605':
                continue
            line = str(k1) + ',' + str(v2[0]) + ',' + str(v2[1]) + ',' + str(v2[2])
            fout.write(line + '\n')
    fout.close()

if __name__ == "__main__":

    inputFile = sys.argv[1]
    outputpath = sys.argv[2]

    '''
    Divid the logs by (device, carrier) pair and sort logs in each 
    (device, carrier) pair by time.
    
    device_seq: dict {device_carrier: [log1_path, log2_path, ...]} logs here are sorted by time
    '''
    dev_car_seq = sortByTime(inputFile)
    # for dev_car, loglist in dev_car_seq.items():
        # print(dev_car, end='\t')
    
    '''
    Store log data in a dictionary
    '''
    print('Loading logs...')
    segDict = segLog(inputFile)

    '''
    Scan logs, extract configs
    '''
    print('Scanning logs, collecting configs...')
    extractConfig(segDict, dev_car_seq)

    '''
    Print the result
    '''
    printer(outputpath)





