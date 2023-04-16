
import ast
import datetime
import traceback
import os, sys
import re

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

__all__ = ["StatAnalyzerLa"]

time_digits = 1

class StatAnalyzerLa:
	def __init__(self, f):
		self.serving_cellset_trace = {}
		self.serving_cell_trace = {}
		self.pcell_trace = {}
		self.cell_trace = {}

		self.valid_cell_change_flag = 0
		self.current_cell_set = []
		self.first_ts = None

		self.last_ho_ts = None
		self.last_ts = None
		self.ho_flag = 0

		self.pcell = []
		self.lte_scell_list = []
		self.nr_scell_list = []

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

	def __cell_change(self, ts):

		t = round(ts, time_digits)

		if len(self.pcell) < 2:
			return

		serving_cellset = [[self.pcell[1], self.pcell[0]]]
		for item in self.lte_scell_list:
			serving_cellset.append([item[1], item[0]])
		for item in self.nr_scell_list:
			serving_cellset.append([item[1], item[0]])

		pcell_str = self.pcell[1] + '-' + self.pcell[0]
		if pcell_str not in self.pcell_trace:
			self.pcell_trace[pcell_str] = [self.pcell[1], self.pcell[0], 0]
		self.pcell_trace[pcell_str][2] += 1

		serving_cellset_str = ''
		for item in serving_cellset:
			if item[1] == 'None':
				continue
			cell_str = item[1] + '-' + item[0]
			if cell_str not in self.serving_cell_trace:
				self.serving_cell_trace[cell_str] = [item[1], item[0], 0]
			self.serving_cell_trace[cell_str][2] += 1
			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [item[1], item[0], 0]
			self.cell_trace[cell_str][2] += 1

			serving_cellset_str += cell_str + '/'
		serving_cellset_str = serving_cellset_str.strip('/')
		if serving_cellset_str not in self.serving_cellset_trace:
			self.serving_cellset_trace[serving_cellset_str] = 0
		self.serving_cellset_trace[serving_cellset_str] += 1

		self.ho_flag = 0

	def __active_handoff(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 7:
			return

		self.pcell_change_flag = 1

		self.pcell = [items[5], items[6]]
		self.lte_scell_list = []
		self.nr_scell_list = []

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __add_nr_cell(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 5:
			return

		self.pcell_change_flag = 1

		self.nr_scell_list.append([items[5], items[6]])

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __rrc_connection_setup_complete(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 7:
			return

		self.pcell_change_flag = 1

		self.pcell = [items[5], items[6]]
		self.lte_scell_list = []
		self.nr_scell_list = []

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __rrc_connection_reestablishment_complete(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 7:
			return

		self.pcell_change_flag = 1

		self.pcell = [items[5], items[6]]
		self.lte_scell_list = []
		self.nr_scell_list = []

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __add_nr_cell(self, ts, line):
		items = line.strip().split()

		# Get source and target
		
		if len(items) < 7:
			return

		self.pcell_change_flag = 1

		self.pcell = [items[5], items[6]]

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __scell_to_add(self, ts, line):

		target = line.strip('')
		matchObj = re.match(r"(.*) {'sCellIndex': '(.*)', 'physCellId': '(.*)', 'dlCarrierFreq': '(.*)'}", target, re.M|re.I)
		cid = matchObj.group(3)
		freq = matchObj.group(4)

		#print([cid, freq])

		self.lte_scell_list.append([cid, freq])

		self.last_ho_ts = ts
		self.ho_flag = 1

	def __serv_cell_meas(self, ts, line):
		# 2020-02-07 18:09:17.331445 [servingCellMeas] 1_SCell 363 2425 413 1150 -99.8125 -14.625
		items = line.strip().split()
		try:
			cid = items[6]
			freq = items[7]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_intra_serv(self, ts, line):
		# 2020-03-01 01:23:18.082748 [connectedIntraServing] PCell 197 850 197 850 -93.1875 -11.25
		items = line.strip().split()
		try:
			cid = items[6]
			freq = items[7]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_intra_neigh(self, ts, line):
		# 2020-05-27 11:06:21.250859 [connectedIntraNeighbor] PCell 411 976 418 976 -111.6875
		items = line.strip().split()
		try:
			cid = items[6]
			freq = items[7]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_inter_neigh(self, ts, line):
		# 2020-09-06 19:53:31.751687 [connectedInterNeighbor] 457 850 87 2000 -110.5625 -13.875
		items = line.strip().split()
		try:
			cid = items[5]
			freq = items[6]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_nr_meas_neigh(self, ts, line):
		# 2021-04-07 17:49:57.953765 [NR_measurementReport] reportNeighborCell 190 2259995 {'event_type': 'a2', 'threshold': -96, 'hyst': 0.0, 'triggerQuantity': 'rsrp', 'report_id': 3} serving: -11.0 -104 target: -11.5 -99 190 2259995 387 850
		items = line.strip().split()
		try:
			cid = items[4]
			freq = items[5]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_meas_nr_neigh(self, ts, line):
		# 2021-04-07 18:02:47.202525 [measurementReport] reportNRNeighborCell 189 2259995 {'event_type': 'b1_nr', 'threshold': -110, 'hyst': 0.0, 'reportInterval': None, 'reportAmount': None, 'timeToTrigger': None, 'triggerQuantity': 'rsrp', 'report_id': '6'} serving: -15.5 -80 target: -10.5 -93 311 850
		items = line.strip().split()
		try:
			cid = items[4]
			freq = items[5]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1
		except:
			print("Exception in measurement report:", line)
			return

	def __conn_meas_nr_serv(self, ts, line):
		# 2021-04-07 18:55:00.837992 [measurementReport] reportNRServingCell 190 2259995 {'event_type': 'a3', 'offset': 3.0, 'hyst': 1.0, 'reportInterval': 'ms480', 'reportAmount': 'infinity', 'timeToTrigger': 'ms80', 'triggerQuantity': 'rsrq', 'report_id': '1'} serving: -17.0 -90 target: -10.5 -83 387 850
		items = line.strip().split()

		try:
			cid = items[4]
			freq = items[5]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1

		except:
			print("Exception in measurement report:", line)
			return

	def __conn_meas_nr_ml1_searcher(self, ts, line):
		# 2022-11-07 20:05:21.228276 [NrMl1SearcherMeasurementDatabaseUpdate] 880 527790 547 527790 -117.281 -18.609
		items = line.strip().split()

		try:
			cid = items[5]
			freq = items[6]
			cell_str = str(freq) + '-' + str(cid)

			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [freq, cid, 0]
			self.cell_trace[cell_str][2] += 1

		except:
			print("Exception in measurement report:", line)
			return

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

						self.last_ts = ts
					else:
						ts = self.last_ts

				if '[activeHandoff]' in line:
					self.__active_handoff(ts, line)

				if '[addNRCell]' in line:
					self.__add_nr_cell(ts, line)

				if 'rrcConnectionSetupComplete' in line:
					self.__rrc_connection_setup_complete(ts, line)

				if 'RRCConnectionReestablishmentComplete' in line:
					self.__rrc_connection_reestablishment_complete(ts, line)

				if 'mobilityControlInfo_element' in line:
					self.lte_scell_list = []

				if 'SCellToAddMod' in line:
					self.__scell_to_add(ts, line)

				if self.ho_flag and self.last_ho_ts != self.last_ts:
					self.__cell_change(ts)

				if '[servingCellMeas]' in line:
					self.__serv_cell_meas(ts, line)

				if '[connectedIntraServing]' in line:
					self.__conn_intra_serv(ts, line)

				if '[connectedIntraNeighbor]' in line:
					self.__conn_intra_neigh(ts, line)

				if '[connectedInterNeighbor]' in line:
					self.__conn_inter_neigh(ts, line)

				if '[NR_measurementReport] reportNeighborCell' in line:
					self.__conn_nr_meas_neigh(ts, line)

				if '[measurementReport] reportNRNeighborCell' in line:
					self.__conn_meas_nr_neigh(ts, line)

				if '[measurementReport] reportNRServingCell' in line:
					self.__conn_meas_nr_serv(ts, line)

				if '[NrMl1SearcherMeasurementDatabaseUpdate]' in line:
					self.__conn_meas_nr_ml1_searcher(ts, line)

