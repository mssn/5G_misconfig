################################################
#   Datasets and source codes for CoNEXT'23 
#   (Dependent Misconfiguration in 5G/4.5G Radio Resource Control)
#
################################################

This README is used to introduce our released datasets and source codes by our CoNEXT'23 work: 
“Dependent Misconfiguration in 5G/4.5G Radio Resource Control”.

We have conducted a reality check on dependent misconfiguration with 4.5G/5G datasets from three US operators and one China operator. We use one 5G phone model (Google Pixel 5) to collect US datasets in Los Angles, Chicago, Indianapolis and West Lafayette with three top-tier carriers in the US (AT&T, Verizon and T-Mobile). We also use a dataset with 4G traces collected from one operator in China.

This reality check has covered 26,618 serving cells (4G: 25,005 and 5G: 1,613) out of 48,249 cells (4G: 44,696 and 5G: 3,553). In this study, all three US operators run 5G in a non-standard-alone (NSA) mode. We have collected data speed results through file downloading experiments in the US.

1) Structure of files

├── dataset_stat.csv
├── misconfig_stat.csv 
├── code
│   └── misconfig_detector
│       ├── misconfig_d1.py
│       ├── misconfig_d2_missed_4g.py
│       ├── misconfig_d2_missed_5g.py
│       ├── misconfig_d3.py
│       ├── misconfig_d4.py
│       ├── misconfig_d5.py
│       ├── misconfig_stat_merge.py
│       └── misconfig_stat_table_generator.py
│
└── dataset
    ├── config
    │   ├── csm
    │   │   ├── cfg_{area}.txt
    │   │   ├── cfg_idle_{area}.txt
    │   │   └── cfg_measgap_{area}.txt
    │   └── dsm
    │       ├── delta_cfg_{area}.txt
    │       └── delta_cfg_{area}_missed_4g.txt
    └── misconfig
        ├── misconfig_d1-a1a2_{area}_{operator}.csv
        ├── misconfig_d1-b1a2_{area}_{operator}.csv
        ├── misconfig_d2-missed_4g_{area}_{operator}.csv
        ├── misconfig_d2-missed_5g_{area}_{operator}.csv
        ├── misconfig_d3_{area}_{operator}.csv
        ├── misconfig_d4_{area}_{operator}.csv
        └── misconfig_d5_{area}_{operator}.csv


2) Code Descriptions

-------------------------------------------------------------------------------
code/misconfig_detector/misconfig_d*.py: 
Detect and output misconfiguration instances (D1-D5).

Command:
$ python3 misconfig_d*.py {input file path} {output folder}
-------------------------------------------------------------------------------
code/misconfig_detector/misconfig_stat_merge.py: 
Merge and adjust the format of misconfiguration instance lists

Command:
$ python3 misconfig_stat_merge.py $dataset/misconfig {output file path}
-------------------------------------------------------------------------------
code/misconfig_detector/misconfig_stat_table_generator.py: 
Output the statistics of misconfiguration instances.

Command:
$ python3 misconfig_stat_table_generator.py $dataset/misconfig {output file path}
-------------------------------------------------------------------------------

3) Dataset Descriptions

-------------------------------------------------------------------------------
dataset/config:
The configuration traces generated by csm_generator.py and the delta configuration traces generated by dsm_generator.py.

cfg_{area}.txt, cfg_idle_{area}.txt and cfg_measgap_{area}.txt are used as the input file to detect d3, d4 and d5 instances respectively.
-------------------------------------------------------------------------------
dataset/misconfig:
The list of detected misconfiguration instances for each region and operator. For each instance, information such as operator, PCell id, PCell channel, and misconfigured channels are included.
-------------------------------------------------------------------------------

