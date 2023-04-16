import os
from collections import defaultdict
import re
import operator
import sys

car = ''
counter = {}

def extractConfig(f):
    global counter
    #counter = {} # carrier: frequency: measstate: cnt
    last_meas_state = set()
    one_meas_state = set()
    last_ts = None
    pcell_str = None
    #counter[car] = {}
    with open(f, 'r', encoding='utf-8-sig') as lines:
        for line in lines:
            if line.find('lat') >= 0:
                continue

            items = line.strip().split(',')

            ts = float(items[0])
            if last_ts and ts != last_ts:
                one_meas_state = frozenset(one_meas_state)
                if len(last_meas_state) > 0:
                    added_meas = set()
                    added_meas = one_meas_state.difference(last_meas_state)

                    removed_meas = set()
                    removed_meas = last_meas_state.difference(one_meas_state)

                    delta_state = [added_meas, removed_meas]
                    delta_state_union = added_meas.union(removed_meas)

                    if one_meas_state:
                        if len(delta_state_union) > 0:
                            if pcell_str not in counter[car]:
                                counter[car][pcell_str] = {}
                            if delta_state_union not in counter[car][pcell_str]:
                                counter[car][pcell_str][delta_state_union] = [delta_state, 0]
                            counter[car][pcell_str][delta_state_union][1] += 1

                last_meas_state = one_meas_state.copy()
                one_meas_state = set()

            pcell_str = items[18] + '-' + items[17]
            freq = items[5]

            if items[5] == items[18]:
                freq += '_P'
            else:
                freq += '_S'

            event = items[14]
            threshold1 = items[15]
            if len(items[15]) == 0:
                threshold1 = 'None'
            threshold2 = items[16]
            if len(items[16]) == 0:
                threshold2 = 'None'
            threshold = threshold1 + '_' + threshold2
            htss = items[8]
            if len(items[8]) == 0:
                htss = 'None'
            ttt = items[9]
            if len(items[9]) == 0:
                ttt = 'None'

            meas_str = freq + ': ' + event + ', thr/ofst: ' + threshold + ', hetersis: ' + htss + ', time_to_trigger: ' + ttt

            one_meas_state.add(meas_str)

            last_ts = ts

def printer(counter, min_cnt = 0):
    for car, freq_deltastate_count in counter.items():
        print('Carrier: ' + car)
        # if car == '310410':
        for freq, deltastate_cnt in freq_deltastate_count.items():
            print('\tFrequency: ' + freq, 'Cnt:', len(deltastate_cnt))
            for k,v in sorted(deltastate_cnt.items(), key=lambda item: item[1], reverse=True):
            # for measstate, cnt in dict(sorted(measstate_cnt.items(), key=operator.itemgetter(1), reverse=True)).items():
                if v[1] > min_cnt:
                    print('\t\tMeasurement delta state count: ' + str(v[1]))
                    print('\t\t\tAdded delta state: ')
                    for cfg in v[0][0]:
                        print('\t\t\t\t' + cfg)
                    print('\t\t\tRemoved delta state: ')
                    for cfg in v[0][1]:
                        print('\t\t\t\t' + cfg)

if __name__ == "__main__":

    inputfolder = sys.argv[1]
    car = sys.argv[2]

    counter[car] = {}

    file_list = []
    for subdir, dirs, files in os.walk(inputfolder):
        for f in files:
            f_path = os.path.abspath(os.path.join(subdir, f))
            if '.csv' in f_path:
                file_list.append(f_path)

    '''
    Scan logs, extract configs
    '''
    for f in file_list:
        extractConfig(f)

        '''
        Print the result
        '''
    printer(counter)
