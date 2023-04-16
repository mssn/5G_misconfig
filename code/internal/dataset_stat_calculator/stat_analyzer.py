
import ast
import datetime
import traceback
import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

__all__ = ["StatAnalyzer"]

time_digits = 1

class StatAnalyzer:
	def __init__(self, f):
		self.serving_cellset_trace = {}
		self.serving_cell_trace = {}
		self.pcell_trace = {}
		self.cell_trace = {}

		self.valid_cell_change_flag = 0
		self.current_cell_set = []
		self.first_ts = None

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

	def __cell_change(self, ts, line):
		items = line.strip().split()

		if len(items) < 35:
			return

		# Get source and target		
		src_cell_set = [items[3], items[4], items[5], items[6], items[7], items[8], items[9], items[10], items[11], items[12], items[13], items[14], items[15], items[16], items[17], items[18]]
		dst_cell_set = [items[19], items[20], items[21], items[22], items[23], items[24], items[25], items[26], items[27], items[28], items[29], items[30], items[31], items[32], items[33], items[34]]

		if len(self.current_cell_set) == 0:
			self.current_cell_set = src_cell_set

		src_freq = [self.current_cell_set[1], self.current_cell_set[3], self.current_cell_set[5], self.current_cell_set[7], self.current_cell_set[9], self.current_cell_set[11], self.current_cell_set[13], self.current_cell_set[15]]
		dst_freq = [dst_cell_set[1], dst_cell_set[3], dst_cell_set[5], dst_cell_set[7], dst_cell_set[9], dst_cell_set[11], dst_cell_set[13], dst_cell_set[15]]

		if self.current_cell_set == dst_cell_set:
			return

		t = round(ts, time_digits)

		pcell_str = items[20] + '-' + items[19]
		if pcell_str not in self.pcell_trace:
			self.pcell_trace[pcell_str] = [items[20], items[19], 0]
		self.pcell_trace[pcell_str][2] += 1

		serving_cellset_str = ''
		for i in range(0, 8):
			if items[19 + 2*i] == 'None':
				continue
			cell_str = items[19 + 2*i + 1] + '-' + items[19 + 2*i]
			if cell_str not in self.serving_cell_trace:
				self.serving_cell_trace[cell_str] = [items[19 + 2*i + 1], items[19 + 2*i], 0]
			self.serving_cell_trace[cell_str][2] += 1
			if cell_str not in self.cell_trace:
				self.cell_trace[cell_str] = [items[19 + 2*i + 1], items[19 + 2*i], 0]
			self.cell_trace[cell_str][2] += 1

			serving_cellset_str += cell_str + '/'
		serving_cellset_str = serving_cellset_str.strip('/')
		if serving_cellset_str not in self.serving_cellset_trace:
			self.serving_cellset_trace[serving_cellset_str] = 0
		self.serving_cellset_trace[serving_cellset_str] += 1

		self.current_cell_set = dst_cell_set

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

				if 'nr-rrc.rrc_reconf' in line or '[activeHandoff]' in line or 'mobilityControlInfo_element' in line or 'addNRCell' in line or 'NRRRCSetupComplete' in line or 'RRCConnectionSetup' in line or 'NRRRCReconfigurationComplete' in line or 'RRCConnectionReestablishment' in line or '[NrMacUlPhysicalChannelScheduleReport]' in line or '[rrcConnectionRelease]' in line or '[SCGFailure]' in line or '[releaseNRCell]' in line:
					self.valid_cell_change_flag = 1
				if '[Cellsetchange]' in line:
					if self.valid_cell_change_flag == 1:
						self.__cell_change(ts, line)
					self.valid_cell_change_flag = 0

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

