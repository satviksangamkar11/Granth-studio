#!/bin/bash
# usage: file_regen.sh <shot_id> <vNN> <edit_id>
# Files the download whose NAME carries this exact title (D:/aai work/flow_outputs/<shot>__<vNN>_2K_*.jpg, newest). FAILS CLOSED if there is none (no guessing: two agents
# downloading at once once mis-filed an image). After an EDIT the tile keeps its old title: then call file_flow_download.py directly with the explicit raw path.
S=$1; V=$2; EID=$3
cd "D:/aai work"
T=$(ls -t "D:/aai work/flow_outputs/${S}__${V}"_2K_*.jpg 2>/dev/null | head -1)
if [ -z "$T" ]; then echo "ERROR: no download named ${S}__${V}_2K_*.jpg in D:/aai work/flow_outputs (repeat the 2K download, or file an edit download with file_flow_download.py and its explicit path)"; exit 1; fi
REFS=$(python -c "
import json
j=[x for x in json.load(open('D:/aai work/granthstudio/canon/drafts/A1_flow_regen_jobs.json',encoding='utf-8')) if x['shot_id']=='$S'][0]
print('|'.join(j['characters']+([j['place_search']] if j['place_search'] else [])+['ref_temple']))") || { echo "ERROR: $S not in A1_flow_regen_jobs.json"; exit 1; }
PYTHONIOENCODING=utf-8 python "D:/aai work/granthstudio/scripts/flow/file_flow_download.py" "$T" $S $V "edit/$EID" "$REFS" "regen chosen by agent" shots
