"""Recover firmware and parameters from a preserved PX4 ULog, offline only."""
import argparse, hashlib, json
from pathlib import Path
import importlib.metadata
from pyulog import ULog

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--input',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
u=ULog(str(a.input),message_name_filter_list=['vehicle_local_position','vehicle_status','vehicle_land_detected','vehicle_local_position_setpoint','estimator_status'])
effective=dict(u.initial_parameters)
changes=[]
for timestamp,name,value in u.changed_parameters:
    changes.append({'ulog_timestamp_us':int(timestamp),'name':name,'value':value})
    effective[name]=value
params={'source':str(a.input.resolve()),'meaning':'PX4 configuration, not CopterSim physical model calibration','initial':u.initial_parameters,'changes':changes,'effective_at_log_end':effective}
(a.output/'B1-px4-parameters.json').write_text(json.dumps(params,indent=2)+'\n')
topics=[]
for d in u.data_list:
    ts=d.data.get('timestamp',[])
    topics.append({'name':d.name,'multi_id':d.multi_id,'samples':len(ts),'first_timestamp_us':int(ts[0]) if len(ts) else None,'last_timestamp_us':int(ts[-1]) if len(ts) else None})
summary={'source':str(a.input.resolve()),'bytes':a.input.stat().st_size,'sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'parser':'pyulog '+importlib.metadata.version('pyulog'),'info':u.msg_info_dict,'release_fields':u.get_version_info(),'start_timestamp_us':u.start_timestamp,'last_timestamp_us':u.last_timestamp,'native_span_s':(u.last_timestamp-u.start_timestamp)/1e6,'clock_meaning':'ULog/PX4 native microseconds. time_ref_utc=0, no verified UTC correspondence. Startup plus flight, not a flight-only duration.','initial_parameter_count':len(u.initial_parameters),'parameter_change_count':len(changes),'dropout_record_count':len(u.dropouts),'file_corruption_reported':u.file_corruption,'selected_topics':topics,'interpretation':'vehicle_local_position remains a PX4 estimate. Firmware identifier does not prove an unmodified source/build. Early parameter changes do not identify the responsible launcher.'}
(a.output/'native-log-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['bytes','native_span_s','initial_parameter_count','parameter_change_count','file_corruption_reported']}))
