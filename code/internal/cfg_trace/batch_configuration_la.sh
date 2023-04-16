# sh batch_instance_final.sh folderSRC indy_path exp_range_tag grid_size
folderSRC=$1
indyfolder=$2
cfgcodefolder="$folderSRC/cfg_trace"
tagdatafolder="$indyfolder/tagData"
locfolder="$indyfolder/raw_loc"
intermfolder="$indyfolder/interm"
region_range_file="$intermfolder/region_range.csv"

cd $indyfolder/raw_cfg
mkdir att
cd att

tag=("INDY-0405" "INDY-0407" "INDY-0419" "INDY-0423" "INDY-0501" "INDY-0501-UDP" "INDY-0511" "INDY-0513" "INDY-0517" "INDY-0520" "INDY-0524" "INDY-0527" "INDY-0531" "INDY-0603" "INDY-0607" "INDY-0618-ch" "INDY-0619-r2" "INDY-0625" "INDY-0627" "INDY-0701" "INDY-0707" "INDY-0709" "INDY-0714" "INDY-0715" "INDY-0716" "INDY-0725" "INDY-0728" "INDY-0805" "INDY-0807" "INDY-0930" "INDY-1009" "INDY-1017" "INDY-1209" "INDY-1211" "INDY-1224" "INDY-1226" "INDY-0120" "INDY-0122" "INDY-0127")

for item in ${tag[*]}
do
 mkdir $item
 cd $item
 python3 "$cfgcodefolder/main_cfg_la.py" "$tagdatafolder/$item" "310410"
 cd ..

done