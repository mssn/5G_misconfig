# check whether A6 is reported from a weaker cell to a better cell

import sys

neigh_rsrp = 0
scell1_rsrp = 0
scell2_rsrp = 0
a6 = False
GPS = None
check_add = False
for line in open(sys.argv[1]).readlines():
	if ' a6 ' in line:
		# 2020-10-21 22:51:03.015009 Measurement report 17 a6 325 -94 -13.5 325 -109 -15.5 , Scell: 52 -115 -20.0 
		blocks = line.split()
		#if len(blocks) < 11:
		#print(line)
		# print line
		try:
			neigh_rsrp = int(blocks[9][1:])
		except:
			continue
		if blocks.count('Scell:') > 1:
			scell2_rsrp = int(blocks[-1][1:])
			scell1_rsrp = int(blocks[-5][1:])
		else:
			scell1_rsrp = int(blocks[-1][1:])
			scell2_rsrp = 0
		a6 = True
		a6_line = line
		
	elif 'Remove' in line:
		if not a6:
			continue
		a6 = False
		# print line.split()[1]
		if line.split()[1] == '1':
			# print a6_line, scell1_rsrp, neigh_rsrp
			if scell1_rsrp <= neigh_rsrp: # or scell1_rsrq < neigh_rsrq:
				#print(GPS)
				print(a6_line)
				#print('1', scell1_rsrp, neigh_rsrp)
				check_add = True
		elif line.split()[1] == '2':
			if scell2_rsrp <= neigh_rsrp: # or scell2_rsrq < neigh_rsrq:
				#print(GPS)
				print(a6_line)
				#print('2', scell2_rsrp, neigh_rsrp)
				check_add = True
	elif 'Add' in line:
		if not check_add:
			continue
		#print('added', a6_line)
		# print a6_line
		check_add = False
	elif 'Location' in line:
		GPS = line
	elif '2020' in line:
		if not a6:
			check_add = False



