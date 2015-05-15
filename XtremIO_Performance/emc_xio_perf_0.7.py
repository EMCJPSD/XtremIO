#!/usr/bin/python
import time
import json
import commands
import sys
import os
import urllib2
import base64



## Define parameter headings
clusters_met=['space-in-use','logical-space-in-use','thin-provisioning-ratio','ud-ssd-space','ud-ssd-space-in-use','dedup-space-in-use','dedup-ratio','dedup-ratio-text','wr-bw','wr-iops','rd-bw','rd-iops','bw','iops','wr-latency','rd-latency','avg-latency','acc-num-of-rd','acc-num-of-wr','acc-size-of-rd','acc-size-of-wr']
volumes_met=['wr-bw','wr-iops','rd-bw','rd-iops','bw','iops','logical-space-in-use','vol-size','wr-latency','rd-latency','avg-latency']
targets_met=['iops', 'rd-iops', 'wr-iops', 'bw', 'rd-bw', 'wr-bw']
initiators_met=['iops', 'rd-iops', 'wr-iops', 'bw', 'rd-bw', 'wr-bw']
ssds_met=['iops', 'rd-iops', 'wr-iops', 'bw', 'rd-bw', 'wr-bw','percent-endurance-remaining']
xenvs_met=['cpu-usage']

##
## send HTTP Request with Python LIB
##
def sendRequest(c_name):
	req=urllib2.Request(c_name)
	strAuth="admin:Xtrem10"
	req.add_header("Authorization","Basic "+base64.encodestring(strAuth))
	resp=urllib2.urlopen(req)
	return resp.read()
##
## Output the defined parameters for the designated object to file in csv format
## File name will be in object_name.csv format
##
def get_performance(c_name):
	global f_count

	## Create directories for output files if they do not exist
	c_dir="csv_running/"+c_name+"/"
	if not os.path.exists('csv_running'):
		os.mkdir('csv_running')
	if not os.path.exists(c_dir):
		os.mkdir(c_dir)

	## Obtain list of child objects
	#these two line is for linux
	url="https://10.16.44.85/api/json/types/"+c_name
	resp=sendRequest(url)
	result=json.loads(resp)

	## Copy the parameter headings to be used for the designated object
	if c_name=="volumes":
		met=volumes_met
	elif c_name=="clusters":
		met=clusters_met
	elif c_name=="targets":
		met=targets_met
	elif c_name=="initiator-groups":
		met=initiators_met
	elif c_name=="ssds":
		met=ssds_met
	elif c_name=="xenvs":
                met=xenvs_met

	## Loop for each child object found
	for i in range(len(result[c_name])):

		## Obtain list of parameters and their value
		resp=sendRequest(result[c_name][i]['href'])
		c_result=json.loads(resp)

		## Open/create csv file, determine whether file needs to be created
		c_filename=c_dir+result[c_name][i]['name']+".csv"
		if not os.path.exists(c_filename):
			c_newfile=1
		else:
			c_newfile=0
		c_file=open(c_filename,'a')

		## Write headings to file if newly created
		if c_newfile==1:
			c_string=""
			for j in range(len(met)):
				if j==0:
					c_string="time, "+met[j]
				else:
					c_string=c_string+", "+met[j]
			print>>c_file,c_string

		## Write/append each parameter value to file
		c_string=""
		for j in range(len(met)):
			if j==0:
				c_string=strtime+", "+c_result['content'][met[j]]
			else:
				c_string=c_string+", "+str(c_result['content'][met[j]])
		print>>c_file,c_string
		f_count=f_count+1
	return 0

##
## Print usage for this script
##
def print_usage():
	print u"Usage: python %s [all|clusters|volumes|targets|initiators|ssds|xenvs] [delay] [count]\n" % argvs[0]
	quit()
	return 0

##
## Execute based on specified option
##
def run_perf(c_option):
	if c_option=="all":
		get_performance('clusters')
		get_performance('volumes')
		get_performance('targets')
		get_performance('initiator-groups')
		get_performance('ssds')
                get_performance('xenvs')
	elif c_option=="clusters":
		get_performance('clusters')
	elif c_option=="volumes":
		get_performance('volumes')
	elif c_option=="targets":
		get_performance('targets')
	elif c_option=="initiators":
		get_performance('initiator-groups')
	elif c_option=="ssds":
		get_performance('ssds')
        elif c_option=="xenvs":
                get_performance('xenvs')
	return 0


##
## Main
## 

argvs=sys.argv

if len(argvs)!=2 and len(argvs)!=3 and len(argvs)!=4: 
	print_usage()
if argvs[1]!="all" and argvs[1]!="clusters" and argvs[1]!="volumes" and argvs[1]!="targets" and argvs[1]!="initiators" and argvs[1]!="ssds" and argvs[1]!="xenvs":
	print_usage()

if len(argvs)==2:
	f_count=0
	strtime=time.strftime('%Y-%m-%d %H:%M:%S')
	run_perf(argvs[1])
	print strtime+" : Update complete. "+str(f_count)+" files updated."
elif len(argvs)==3:
	while True:
		f_count=0
		strtime=time.strftime('%Y-%m-%d %H:%M:%S')
		run_perf(argvs[1])
		print strtime+" : Update complete. "+str(f_count)+" files updated. Waiting "+argvs[2]+" seconds for next."
		time.sleep(float(argvs[2]))
elif len(argvs)==4:
	r_count=int(argvs[3])
	while r_count>0:
		f_count=0
		r_count=r_count-1
		strtime=time.strftime('%Y-%m-%d %H:%M:%S')
		run_perf(argvs[1])
		print strtime+" : Update complete. "+str(f_count)+" files updated. Waiting "+argvs[2]+" seconds for next. Running "+str(r_count)+" more times(s)."
		time.sleep(float(argvs[2]))
		
#final rename the Folder
if os.path.exists('csv_running'):
	strtime=time.strftime('%Y%m%d%H%M%S')
	os.rename('csv_running', 'csv_'+strtime)
