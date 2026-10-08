#!/usr/bin/env python3
"""Replay identical real image-RPC wire bytes through legacy and active decoders."""
import argparse,hashlib,importlib.util,json,sys,time,types
from pathlib import Path
import msgpack,numpy as np
p=argparse.ArgumentParser();p.add_argument('payload',type=Path);p.add_argument('legacy_source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
payload=a.payload.read_bytes()
package=types.ModuleType('legacy_msgpack');package.__path__=[str(a.legacy_source)];sys.modules['legacy_msgpack']=package
for name in ['exceptions','fallback']:
 spec=importlib.util.spec_from_file_location('legacy_msgpack.'+name,a.legacy_source/(name+'.py'));module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
legacy=sys.modules['legacy_msgpack.fallback']
def decode(cls,kwargs):
 start=time.perf_counter();decoder=cls(**kwargs);decoder.feed(payload);objects=list(decoder);elapsed=time.perf_counter()-start
 # The intercepted image-client stream can contain only the image result; filter explicit RGB/depth schema.
 images=[]
 for response in objects:
  if isinstance(response,list) and len(response)==4 and isinstance(response[-1],list):
   images.extend(x for x in response[-1] if isinstance(x,dict) and 'image_data_float' in x)
 assert len(images)==10,len(images)
 return images,elapsed
old,old_s=decode(legacy.Unpacker,{'encoding':'utf-8'});new,new_s=decode(msgpack.Unpacker,{'raw':False})
checks=[]
for i,(x,y) in enumerate(zip(old,new)):
 assert x['width']==y['width'] and x['height']==y['height']
 rgb_equal=x['image_data_uint8']==y['image_data_uint8']
 dx=np.asarray(x['image_data_float'],np.float32);dy=np.asarray(y['image_data_float'],np.float32)
 depth_equal=np.array_equal(dx,dy,equal_nan=True)
 assert rgb_equal and depth_equal
 checks.append({'response_index':i,'width':x['width'],'height':x['height'],'rgb_bytes_equal':rgb_equal,'depth_float32_equal':depth_equal,'rgb_sha256':hashlib.sha256(y['image_data_uint8']).hexdigest(),'depth_float32_sha256':hashlib.sha256(dy.tobytes()).hexdigest()})
record={'payload_path':str(a.payload),'payload_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'legacy_implementation':legacy.Unpacker.__module__,'active_version':msgpack.version,'active_implementation':msgpack.Unpacker.__module__,'active_file':msgpack.__file__,'legacy_source_sha256':hashlib.sha256((a.legacy_source/'fallback.py').read_bytes()).hexdigest(),'legacy_decode_wall_s':old_s,'active_decode_wall_s':new_s,'timing_sample_count':1,'timing_scope':'same settled 5-view RGB/depth MessagePack response payload decode only; instrumented CPU wall time','equivalence':checks}
a.output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='equivalence'},indent=2))
