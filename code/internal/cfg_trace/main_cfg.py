import collections
import os
import sys
import math
import pandas as pd

from cfg_parser import CfgParser

loc_time_digits = 2

cfg_trace = []

region_range = {}

cur_mccmnc = None

def check_mccmnc(filetag, mccmnc):
	if filetag.find('202104') >= 0 or filetag.find('202105') >= 0:
		if mccmnc == "310410":
			return 1
		else:
			return 0

	if mccmnc == '310410':
		if filetag.find('-a-') >= 0:
			return 1
		else:
			return 0
	elif mccmnc == '311480':
		if filetag.find('-v-') >= 0:
			return 1
		else:
			return 0
	elif mccmnc == '310260':
		if filetag.find('-t-') >= 0:
			return 1
		else:
			return 0

	'''
	for subdir, dirs, files in os.walk(tas_dir):
		for f in files:
			path = os.path.abspath(os.path.join(subdir, f))
			if 'diag_' in path and filetag in path:
				print(path)
				temp = str(f).split('diag_log_')[1].split('_')[4].split('.')[0]
				if temp and temp != mccmnc:
					return 0
				elif temp and temp == mccmnc:
					return 1
	'''
	return 0

def prepare_data(tag):
	global cfg_trace
		
	df = pd.DataFrame(cfg_trace, columns=['timestamp', 'lat', 'lon', 'operator', 'region', 'config_freq', 'rat_type', 'rrc_type', 'hyst', 'timeToTrigger', 'reportInterval', 'reportAmount', 'triggerQuantity', 'maxReportCells', 'event_type', 'threshold1', 'threshold2', 'pcell_cid', 'pcell_freq', 'nrscell_cid', 'nrscell_freq', 'pcell_change_flag', 'last_report_type'])
	df.to_csv('cfg_trace_' + tag + '.csv', index=False, na_rep='None')

def handle_taskround_directory(taskround, tagdata, locfile):
	global cfg_trace
	print("Handle taskround", taskround)
	parser = CfgParser(tagdata, locfile, cur_mccmnc, region_range)
	cfg_trace = parser.cfg_trace

	tag = os.path.basename(os.path.normpath(taskround))
	prepare_data(tag)

def parse_taskrounds(tagdata_dir, loc_dir, region_range_file):
	global region_range

	with open(region_range_file,'r') as lines:
		for line in lines:
			if line.startswith('area_id'):
				continue
			items = line.strip().split(',')
			region_id = items[0]
			gps_range = [float(items[1]), float(items[2]), float(items[3]), float(items[4])]
			if region_id not in region_range:
				region_range[region_id] = [gps_range]
			else:
				region_range[region_id].append(gps_range)

	for subdir, dirs, files in os.walk(tagdata_dir):
		for name in files:
			taskround = str(name).split('tagData_')[1].split('.txt')[0]
			if cur_mccmnc != "all" and check_mccmnc(taskround, cur_mccmnc) == 0:
				continue
			print(name)
			filename = 'tagData_' + taskround + '.txt'
			tagdata = os.path.join(tagdata_dir, str(name))
			filename = 'location_trace_' + taskround + '.csv'
			locfile = os.path.join(loc_dir, filename)
			if not os.path.isfile(locfile):
				print('Location file missing:', locfile)
				continue

			handle_taskround_directory(taskround, tagdata, locfile)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage python main.py [directory of all tagData files] [directory of all loc files] [target mccmnc] [region range file]")
		exit()

	cur_mccmnc = sys.argv[3]

	parse_taskrounds(sys.argv[1], sys.argv[2], sys.argv[4])
