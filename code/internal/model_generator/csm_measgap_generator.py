# Usage: python3 count_cell.py mmlab_ny.txt
import sys
import re
from datetime import datetime

def get_ts(l):
    ts = re.compile(r'[0-9]{4}-[0-9]{2}.*\.[0-9]{6}')
    result = ts.search(l)
    if result:
        s = result.group()
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
        return dt
    return None

op = None
cell_list = {}
op_cnt = {}
missing_flag = False
in_meas_config = False
missing_flag_active = False
gci = False

need_line = False
freq_config = {} # {freq: meas}

misconfig_list = {}

cur_ts = None
missing_ts = None
cell_str = None
cid = None
freq = None

print('ts operator freq cid missing_flag_new')

for line in open(sys.argv[1]).readlines():
    # print(line, in_meas_config)

    if 'customPacket' in line:
        continue

    if get_ts(line):
        cur_ts = get_ts(line)
    if 'ECI' in line:
        blocks = line.split()
        gci = blocks[6]
        cell_str = blocks[3] + '-' + blocks[4]
        cid = blocks[4]
        freq = blocks[3]
        # print(line)

    elif 'new log' in line:
        # print(line)
        op = line[-17:-11]
        op = op.strip('_')
        if op not in op_cnt:
            op_cnt[op] = 0
        # if op[0] != '3':
            # print line
    elif 'Suspicious: missing CA meas on some freq. (Edge case: missing obj upon HO)' in line:
        missing_flag = True
        missing_flag_active = False
        if cur_ts:
            missing_ts = cur_ts
    elif 'REQ' in line or 'REEST' in line:
        missing_flag = False
        in_meas_config = False
        missing_flag_active = False

    if 'Measurement control' in line:
        # print '???', line
        in_meas_config = True
        scell_freq_id = {} # {id: freq}
        report_config = {} # {id: config}
        missing_flag_active = False
        # print 

    elif line.startswith('MeasGap'):
        # print line[0]
        in_meas_config = False
        #if gci and gci not in cell_list and missing_flag and missing_flag_active:
        if gci and gci not in cell_list:
            if op_cnt[op] == 1:
                missing_flag_new = False
                if missing_flag and missing_flag_active:
                    missing_flag_new = True
                missed_sample = str(cur_ts) + ' ' + op + ' ' + freq + ' ' + cid + ' ' + str(missing_flag_new)
                print(missed_sample)
                #print(scell_freq_id)
                #print(report_config)
                #print(freq_config)

        # if gci not in cell_list and missing_flag:
            if missing_flag and missing_flag_active:
                cell_list[gci] = blocks[1]
                op_cnt[op] += 1

        missing_flag = False
        missing_flag_active = False
        # print freq_config

    if in_meas_config:
        items = line.split()
        if items[0] == 'LteMeasObjectEutra' and items[4] != 'None':
            scell_freq_id[items[1]] = items[2]
        elif items[0] == 'LteReportConfig':
            need_line = True
            rep_id = items[1]
        elif items[0] == 'MeasObj':
            for scell in scell_freq_id:
                if scell == items[2][2:-2]:
                    if items[3][1] in report_config:
                        freq = scell_freq_id[scell]
                        report = report_config[items[3][1]]
                        if freq not in freq_config:
                            freq_config[freq] = [report]
                        else:
                            if report not in freq_config[freq]:
                                freq_config[freq].append(report)
                        if missing_flag and 'a1' in report:
                            missing_flag_active = True
                            if cur_ts and missing_ts:
                                gap = (cur_ts - missing_ts).total_seconds()
                                #print('LOG', op, gap, missing_ts)
                                #if gap > 1:
                                #print('BUG', cur_ts, line)
                        # print scell_freq_id[scell], report_config[items[3][1]]
        elif need_line and (line[:2] == 'a1' or line[:2] == 'a2'):
            report_config[rep_id] = line[:-1]
            need_line = False

