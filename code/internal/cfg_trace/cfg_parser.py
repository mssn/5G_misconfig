
import ast
import datetime
import traceback
import os, sys
import re

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

__all__ = ["CfgParser"]

class CfgParser:
	def __init__(self, f, loc_file, cur_mccmnc, region_range):
		self.cfg_trace = []
		self.loc_trace = {}

		self.region_range = region_range

		self.cur_mccmnc = cur_mccmnc
		self.operator = ""
		if self.cur_mccmnc == "310410":
			self.operator = "A"
		elif self.cur_mccmnc == "311480":
			self.operator = "V"
		elif self.cur_mccmnc == "310260":
			self.operator = "T"

		self.first_ts = None

		self.current_cell_set = [None,None,None,None]

		self.valid_cell_change_flag = 0

		self.last_report_type = None
		self.pcell_change_flag = 0

		self.last_cfg_ts = None

		self.__load_loc(loc_file)
		self.__load_content(f)
		
	def __time_since_epoch(self, time_str):
		epoch = datetime.datetime.utcfromtimestamp(0)
		try:
			if '.' in time_str:
				ts_tmp = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
			else:
				ts_tmp = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
			return (ts_tmp - epoch).total_seconds()
		except:
			# traceback.print_exc(file=sys.stdout)
			return None

	def check_region(self, lat, lon, operator):

		for k, v in self.region_range.items():
			if k.find(operator) < 0:
				continue
			if k.find("R") < 0:
				continue
			for sub_range in v:
				min_lat = sub_range[0]
				max_lat = sub_range[1]
				min_lon = sub_range[2]
				max_lon = sub_range[3]
				if lon >= min_lat and lon <= max_lat:
					if lat >= min_lon and lat <= max_lon:
						return k
		return "None"

	def __add_new_cfg(self, ts, line):

		# NewCFG:Freq:65535:{'report_id': '1', 'hyst': 1.0, 'timeToTrigger': 'ms640', 'reportInterval': 'ms240', 'reportAmount': 'infinity', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'a3', 'offset': 5.0}]}
		# NewCFG:Freq:65535:{'report_id': '2', 'hyst': 1.0, 'timeToTrigger': 'ms320', 'reportInterval': 'ms240', 'reportAmount': 'infinity', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'a5', 'threshold1': -110, 'threshold2': -109}]}
		# NewCFG:Freq:5035:{'report_id': '5', 'hyst': 0.0, 'timeToTrigger': 'Not Present', 'reportInterval': 'min60', 'reportAmount': 'r1', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'reportStrongestCells'}]}
		# NewCFG:Freq:527790:{'report_id': '6', 'hyst': 1.0, 'timeToTrigger': 'ms256', 'reportInterval': 'min60', 'reportAmount': 'r1', 'triggerQuantity': 'Not Present', 'maxReportCells': '8', 'event_list': [{'event_type': 'b1_nr', 'threshold': -111}]}
		# Freq:677:{'report_id': '7', 'hyst': 0.0, 'timeToTrigger': 'ms40', 'reportInterval': 'min60', 'reportAmount': 'r1', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'a4', 'threshold': -140}]}

		if '[' not in line or ']' not in line:
			return

		endc = line.index('[')
		front = line[:endc-1].strip()
		matchObj = re.match( r"Freq:(.*):{'report_id': '(.*)', 'hyst': (.*), 'timeToTrigger': '(.*)', 'reportInterval': '(.*)', 'reportAmount': '(.*)', 'triggerQuantity': '(.*)', 'event_list':", front, re.M|re.I)

		config_freq = int(matchObj.group(1))
		rat_type = ""
		if config_freq > 2000000:
			rat_type = "mw"
		elif config_freq >100000:
			rat_type = "sub6"
		else:
			rat_type = "lte"

		hyst = matchObj.group(3)
		timeToTrigger = matchObj.group(4)
		reportInterval = matchObj.group(5)
		reportAmount = matchObj.group(6)
		triggerQuantity = matchObj.group(7)

		event_type = ""
		threshold1 = ""
		threshold2 = ""

		if 'reportStrongestCells' in line:
			event_type = 'reportStrongestCells'
			threshold1 = ""
			threshold2 = ""
		elif "a1" in line or "a2" in line or "a4" in line or "b1" in line or "b1_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
		elif "a3" in line or "a6" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'offset': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
		elif "a5" in line or "b2" in line or "b2_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold1': (.*), 'threshold2': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = matchObj.group(3)

		ts_round = round(ts, 1)
		lat = None
		lon = None
		region = None
		if ts_round in self.loc_trace:
			lat = self.loc_trace[ts_round][0]
			lon = self.loc_trace[ts_round][1]
			region = self.check_region(lat, lon, self.operator)

		self.cfg_trace.append({'timestamp'	: ts,
			'lat'			: lat,
			'lon'			: lon,
			'region'		: region, 
			'operator'		: self.operator,
			'config_freq'	: config_freq, 
			'rat_type'	: rat_type, 
			'rrc_type'	: "lte",
			'hyst'	: hyst, 
			'timeToTrigger'	: timeToTrigger, 
			'reportInterval'	: reportInterval, 
			'reportAmount'	: reportAmount, 
			'triggerQuantity'	: triggerQuantity,
			'maxReportCells' 	: "",
			'event_type'	: event_type, 
			'threshold1'	: threshold1, 
			'threshold2'	: threshold2,
			'pcell_cid'			: self.current_cell_set[0],
			'pcell_freq'		: self.current_cell_set[1],
			'nrscell_cid'		: self.current_cell_set[2],
			'nrscell_freq'		: self.current_cell_set[3],
			'pcell_change_flag'	: self.pcell_change_flag,
			'last_report_type'	: self.last_report_type,
		})

		if self.last_cfg_ts and ts != self.last_cfg_ts:
			self.last_report_type = None
			self.pcell_change_flag = 0

		self.last_cfg_ts = ts

	def __add_new_lte_nr_cfg(self, ts, line):

		# NewCFG:Freq:65535:{'report_id': '1', 'hyst': 1.0, 'timeToTrigger': 'ms640', 'reportInterval': 'ms240', 'reportAmount': 'infinity', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'a3', 'offset': 5.0}]}
		# NewCFG:Freq:65535:{'report_id': '2', 'hyst': 1.0, 'timeToTrigger': 'ms320', 'reportInterval': 'ms240', 'reportAmount': 'infinity', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'a5', 'threshold1': -110, 'threshold2': -109}]}
		# NewCFG:Freq:5035:{'report_id': '5', 'hyst': 0.0, 'timeToTrigger': 'Not Present', 'reportInterval': 'min60', 'reportAmount': 'r1', 'triggerQuantity': 'rsrp', 'event_list': [{'event_type': 'reportStrongestCells'}]}
		# NewCFG:Freq:527790:{'report_id': '6', 'hyst': 1.0, 'timeToTrigger': 'ms256', 'reportInterval': 'min60', 'reportAmount': 'r1', 'triggerQuantity': 'Not Present', 'maxReportCells': '8', 'event_list': [{'event_type': 'b1_nr', 'threshold': -111}]}

		if '[' not in line or ']' not in line:
			return

		endc = line.index('[')
		front = line[:endc-1].strip()
		matchObj = re.match( r"Freq:(.*):{'report_id': '(.*)', 'hyst': (.*), 'timeToTrigger': '(.*)', 'reportInterval': '(.*)', 'reportAmount': '(.*)', 'triggerQuantity': '(.*)', 'maxReportCells': '(.*)', 'event_list':", front, re.M|re.I)

		config_freq = int(matchObj.group(1))
		rat_type = ""
		if config_freq > 2000000:
			rat_type = "mw"
		elif config_freq >100000:
			rat_type = "sub6"
		else:
			rat_type = "lte"

		hyst = matchObj.group(3)
		timeToTrigger = matchObj.group(4)
		reportInterval = matchObj.group(5)
		reportAmount = matchObj.group(6)
		triggerQuantity = matchObj.group(7)
		maxReportCells = matchObj.group(8)

		event_type = ""
		threshold1 = ""
		threshold2 = ""

		if 'reportStrongestCells' in line:
			event_type = 'reportStrongestCells'
			threshold1 = ""
			threshold2 = ""
		elif "a1" in line or "a2" in line or "a4" in line or "b1" in line or "b1_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
		elif "a3" in line or "a6" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'offset': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
		elif "a5" in line or "b2" in line or "b2_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold1': (.*), 'threshold2': (.*)}]}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = matchObj.group(3)

		ts_round = round(ts, 1)
		lat = None
		lon = None
		region = None
		if ts_round in self.loc_trace:
			lat = self.loc_trace[ts_round][0]
			lon = self.loc_trace[ts_round][1]
			region = self.check_region(lat, lon, self.operator)

		self.cfg_trace.append({'timestamp'	: ts,
			'lat'			: lat,
			'lon'			: lon,
			'region'		: region, 
			'operator'		: self.operator,
			'config_freq'	: config_freq, 
			'rat_type'	: rat_type, 
			'rrc_type'	: "lte",
			'hyst'	: hyst, 
			'timeToTrigger'	: timeToTrigger, 
			'reportInterval'	: reportInterval, 
			'reportAmount'	: reportAmount, 
			'triggerQuantity'	: triggerQuantity, 
			'maxReportCells'	: maxReportCells,
			'event_type'	: event_type, 
			'threshold1'	: threshold1, 
			'threshold2'	: threshold2,
			'pcell_cid'			: self.current_cell_set[0],
			'pcell_freq'		: self.current_cell_set[1],
			'nrscell_cid'		: self.current_cell_set[2],
			'nrscell_freq'		: self.current_cell_set[3],
			'pcell_change_flag'	: self.pcell_change_flag,
			'last_report_type'	: self.last_report_type,
		})

		if self.last_cfg_ts and ts != self.last_cfg_ts:
			self.last_report_type = None
			self.pcell_change_flag = 0

		self.last_cfg_ts = ts

	def __add_new_nr_cfg(self, ts, line):

		# NewCFG:NR_Freq:527790:{'report_id': 1, 'hyst': 1.0, 'event_list': [{'event_type': 'a3', 'offset': 8}], 'triggerQuantity': 'rsrp'}
		# NewCFG:NR_Freq:527790:{'report_id': 3, 'hyst': 1.0, 'event_list': [{'event_type': 'a2', 'threshold': -115}], 'triggerQuantity': 'rsrp'}

		if '[' not in line or ']' not in line:
			return

		endc = line.index('[')
		front = line[:endc-1].strip()
		matchObj = re.match( r"NR_Freq:(.*):{'report_id': (.*), 'hyst': (.*), 'event_list':", front, re.M|re.I)

		config_freq = int(matchObj.group(1))
		rat_type = ""
		if config_freq > 2000000:
			rat_type = "mw"
		elif config_freq >100000:
			rat_type = "sub6"
		else:
			rat_type = "lte"

		hyst = matchObj.group(3)
		timeToTrigger = ""
		reportInterval = ""
		reportAmount = ""
		triggerQuantity = ""

		event_type = ""
		threshold1 = ""
		threshold2 = ""

		if "a1" in line or "a2" in line or "a4" in line or "b1" in line or "b1_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold': (.*)}], 'triggerQuantity': '(.*)'}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
			triggerQuantity = matchObj.group(3)
		elif "a3" in line or "a6" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'offset': (.*)}], 'triggerQuantity': '(.*)'}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = ""
			triggerQuantity = matchObj.group(3)
		elif "a5" in line or "b2" in line or "b2_nr" in line:
			e = line.index('[')
			tail = line[e+1:].strip()
			matchObj = re.match( r"{'event_type': '(.*)', 'threshold1': (.*), 'threshold2': (.*)}], 'triggerQuantity': '(.*)'}", tail, re.M|re.I)
			event_type = matchObj.group(1)
			threshold1 = matchObj.group(2)
			threshold2 = matchObj.group(3)
			triggerQuantity = matchObj.group(4)

		ts_round = round(ts, 1)
		lat = None
		lon = None
		region = None
		if ts_round in self.loc_trace:
			lat = self.loc_trace[ts_round][0]
			lon = self.loc_trace[ts_round][1]
			region = self.check_region(lat, lon, self.operator)

		self.cfg_trace.append({'timestamp'	: ts,
			'lat'			: lat,
			'lon'			: lon,
			'region'		: region,
			'operator'		: self.operator, 
			'config_freq'	: config_freq, 
			'rat_type'	: rat_type, 
			'rrc_type'	: "nr",
			'hyst'	: hyst, 
			'timeToTrigger'	: timeToTrigger, 
			'reportInterval'	: reportInterval, 
			'reportAmount'	: reportAmount, 
			'triggerQuantity'	: triggerQuantity, 
			'maxReportCells' 	: "",
			'event_type'	: event_type, 
			'threshold1'	: threshold1, 
			'threshold2'	: threshold2,
			'pcell_cid'			: self.current_cell_set[0],
			'pcell_freq'		: self.current_cell_set[1],
			'nrscell_cid'		: self.current_cell_set[2],
			'nrscell_freq'		: self.current_cell_set[3],
			'pcell_change_flag'	: self.pcell_change_flag,
			'last_report_type'	: self.last_report_type,
		})

		if self.last_cfg_ts and ts != self.last_cfg_ts:
			self.last_report_type = None
			self.pcell_change_flag = 0

		self.last_cfg_ts = ts

	def __cell_change(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 23:
			return

		src_cell_set = [items[3], items[4], items[5], items[6]]
		dst_cell_set = [items[19], items[20], items[21], items[22]]

		if len(self.current_cell_set) == 0:
			self.current_cell_set = src_cell_set

		self.pcell_change_flag = 0
		if dst_cell_set[0] != self.current_cell_set[0] or dst_cell_set[1] != self.current_cell_set[1]:
			self.pcell_change_flag = 1

		self.current_cell_set = dst_cell_set

	def __load_content(self, f):
		ts = None
		with open(f, 'r') as lines:
			for line in lines:
				items = line.strip().split()

				if (line.startswith('2020-') or line.startswith('2019-') or line.startswith('2021-') or line.startswith('2022-') or line.startswith('2023-')) and len(items) > 1:
					temp = self.__time_since_epoch(items[0] + ' ' + items[1])
					if temp:
						ts = round(temp,6)

						if self.first_ts == None:
							self.first_ts = ts

				if "NewCFG:" not in line:
					if "Freq:" in line and 'report_id' in line and "NR_Freq:" not in line:
						if 'b1_nr' not in line:
							self.__add_new_cfg(ts, line)
						else:
							self.__add_new_lte_nr_cfg(ts, line)
					if "NR_Freq:" in line and 'report_id' in line:
						self.__add_new_nr_cfg(ts, line)

				if 'nr-rrc.rrc_reconf' in line or '[activeHandoff]' in line or '[addNRCell]' in line or 'mobilityControlInfo_element' in line or 'rrcConnectionSetupComplete' in line:
					self.valid_cell_change_flag = 1
				if '[Cellsetchange]' in line:
					if self.valid_cell_change_flag == 1:
						self.__cell_change(ts, line)
					self.valid_cell_change_flag = 0

				if '[measurementReport] reportNRNeighborCell' in line:
					self.__meas_report_nr_neighbor(ts, line)

				if 'NR_measurementReport' in line:
					self.__nr_meas_report_neighbor(ts, line)

				if '[NR_measurementReport] reportNRPCell' in line:
					self.__meas_report_nr_pcell(ts, line)

	def __parse_meas_event(self, line):
		if '{' in line and '}' in line:
			event_type = None
			th1 = None
			th2 = None
			s = line.index('{')
			e = line.index('}')
			meas_dict = ast.literal_eval(line[s:e+1])
			if 'event_type' in meas_dict:
				event_type = meas_dict['event_type']
			if 'threshold' in meas_dict:
				th1 = meas_dict['threshold']
			if 'threshold1' in meas_dict:
				th1 = meas_dict['threshold1']
			if 'offset' in meas_dict:
				th1 = meas_dict['offset']
			if 'threshold2' in meas_dict:
				th2 = meas_dict['threshold2']
			return(event_type, th1, th2)
		return (None,None,None)

	def __meas_report_nr_neighbor(self, ts, line):
		# 2021-04-07 18:58:39.433885 [measurementReport] reportNRNeighborCell 992 2259995 {'event_type': 'b1_nr', 'threshold': -113, 'hyst': 0.0, 'reportInterval': None, 'reportAmount': None, 'timeToTrigger': None, 'triggerQuantity': 'rsrp', 'report_id': '3'} serving: -14.0 -85 target: -11.0 -106 27 850
		items = line.strip().split()

		event_type, th1, th2 = self.__parse_meas_event(line)

		self.last_report_type = event_type

	def __nr_meas_report_neighbor(self, ts, line):
		# 2021-05-24 22:14:10.493789 [NR_measurementReport] reportNeighborCell 587 2264993 {'event_type': 'a2', 'threshold': -113, 'hyst': 0.0, 'triggerQuantity': 'rsrp', 'report_id': 1} serving: -17.0 -114 target: -17.0 -114 587 2259995 227 850
		# 2021-04-07 20:31:24.839213 [NR_measurementReport] reportNeighborCell 642 174300 {'event_type': 'a3', 'offset': 6, 'hyst': 1.0, 'triggerQuantity': 'rsrp', 'report_id': 2} serving: -18.0 -98 target: -13.0 -92 784 174300 49 850
		items = line.strip().split()

		event_type, th1, th2 = self.__parse_meas_event(line)

		self.last_report_type = event_type

	def __meas_report_nr_pcell(self, ts, line):
		# 2021-05-11 18:04:53.086549 [NR_measurementReport] reportNRPCell {'event_type': 'a2', 'threshold': -115, 'hyst': 1.0, 'triggerQuantity': 'rsrp', 'report_id': 1} serving: -13.5 -118 672 174300 355 850
		items = line.strip().split()

		event_type, th1, th2 = self.__parse_meas_event(line)

		self.last_report_type = event_type


	def __load_loc(self, f):
		ts = None
		with open(f, 'r') as lines:
			for line in lines:
				items = line.strip().split(',')

				if line.find('seconds') >= 0:
					continue

				try:
					ts = float(items[0])
					lat = float(items[1])
					lon = float(items[2])

					self.loc_trace[ts] = [lat, lon]
				except:
					print(line)
