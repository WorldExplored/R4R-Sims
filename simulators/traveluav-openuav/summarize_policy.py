#!/usr/bin/env python3
"""Summarize observed policy smoke records, keeping official outputs separate."""
import argparse,collections,json,numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();r=a.run
rows=lambda name:[json.loads(x) for x in (r/name).read_text().splitlines()] if (r/name).exists() else []
trace=rows('policy_trace.jsonl');out=rows('policy_outcomes.jsonl');stage=rows('stage_timings.jsonl');events=rows('controller_events.jsonl');padding=rows('padding_events.jsonl')
lat=[x['policy_waypoint_latency_s'] for x in trace]
process=collections.defaultdict(list)
for line in (r/'gpu-process-samples.log').read_text().splitlines() if (r/'gpu-process-samples.log').exists() else []:
 fields=line.split(',')
 if len(fields)==3:
  try:process[fields[0].strip()].append(float(fields[-1].strip().split()[0]))
  except ValueError:pass
stages={}
for name in sorted(set(x['stage'] for x in stage)):
 times=[x['wall_s'] for x in stage if x['stage']==name];stages[name]={'count':len(times),'first_s':times[0],'steady_mean_s':float(np.mean(times[1:])) if len(times)>1 else None,'all_samples_s':times}
summary={'learned_decisions':len(trace),'budget':10,'outcomes':out,'policy_latency':{'cold_first_s':lat[0] if lat else None,'steady_n':len(lat[1:]),'steady_mean_s':float(np.mean(lat[1:])) if len(lat)>1 else None,'steady_min_s':min(lat[1:]) if len(lat)>1 else None,'steady_max_s':max(lat[1:]) if len(lat)>1 else None,'all_samples_s':lat,'measurement':'same-process CUDA synchronized around coarse+trajectory model.run; preprocessing/DINO/controller/log writes excluded; instrumented'},'assistant_notices':dict(collections.Counter(json.dumps(x['assistant_guidance']) for x in trace)), 'stage_timings':stages,'controller_event_counts':dict(collections.Counter(x['event'] for x in events)),'padding_events':padding,'refined_waypoint_counts':[len(x['refined_waypoints']) for x in trace],'sampled_process_gpu_memory_mib':{pid:{'n':len(vals),'min':min(vals),'max':max(vals)} for pid,vals in process.items()},'process_memory_caveat':'late samples only; process names/PIDs in raw log; not exact isolated policy-only VRAM; model allocator in model_placement.jsonl','official_metrics_denominator':1,'official_eligibility':'budget-truncated one-episode regenerated-metadata assistant-guided smoke; raw official-format metrics, not published benchmark comparison'}
(r/'policy-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['outcomes','padding_events','stage_timings']},indent=2))
