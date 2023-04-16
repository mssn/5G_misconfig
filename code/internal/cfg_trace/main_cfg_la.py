import collections
import os
import sys
import math
import pandas as pd

from cfg_parser_la import CfgParserLa

loc_time_digits = 2

cfg_trace = []

def prepare_data(tag):
	global cfg_trace
		
	df = pd.DataFrame(cfg_trace, columns=['timestamp', 'lat', 'lon', 'operator', 'region', 'config_freq', 'rat_type', 'rrc_type', 'hyst', 'timeToTrigger', 'reportInterval', 'reportAmount', 'triggerQuantity', 'maxReportCells', 'event_type', 'threshold1', 'threshold2', 'pcell_cid', 'pcell_freq', 'nrscell_cid', 'nrscell_freq', 'pcell_change_flag', 'last_report_type'])
	df.to_csv('cfg_trace_' + tag + '.csv', index=False, na_rep='None')

def handle_taskround_directory(tagdata, taskround):
	global cfg_trace
	print("Handle taskround", taskround)
	parser = CfgParserLa(tagdata)
	cfg_trace = parser.cfg_trace

	tag = os.path.basename(os.path.normpath(taskround))
	prepare_data(tag)

def parse_taskrounds(tagdata_dir):

	for subdir, dirs, files in os.walk(tagdata_dir):
		for name in files:
			if name.find('.txt') < 0:
				continue
			print(name)
			taskround = str(name).split('tagData_')[1].split('.txt')[0]
			filename = 'tagData_' + taskround + '.txt'
			tagdata = os.path.join(subdir, str(name))

			handle_taskround_directory(tagdata, taskround)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage python main.py [directory of all tagData files]")
		exit()

	parse_taskrounds(sys.argv[1])
