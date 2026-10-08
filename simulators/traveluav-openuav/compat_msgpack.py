#!/usr/bin/env python3
"""Bridge msgpack-rpc-python 0.4 to author-pinned msgpack 1.1.0 C wheels."""
import difflib,hashlib,json,sys
from pathlib import Path
import msgpack,msgpackrpc.transport.tcp
p=Path(msgpackrpc.transport.tcp.__file__);before=p.read_text()
a='msgpack.Packer(encoding=encodings[0], default=lambda x: x.to_msgpack())'
b='msgpack.Packer(use_bin_type=False, default=lambda x: x.to_msgpack())'
c='msgpack.Unpacker(encoding=encodings[1])';d='msgpack.Unpacker(raw=(encodings[1] is None))'
if a in before and c in before:
 after=before.replace(a,b).replace(c,d);p.write_text(after)
elif b in before and d in before:after=before
else:raise RuntimeError('Unexpected RPC transport source; do not patch blindly')
record=Path(sys.argv[1]);record.mkdir(parents=True,exist_ok=True)
(record/'rpc-compat.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/msgpackrpc/transport/tcp.py',tofile='b/msgpackrpc/transport/tcp.py')))
# Wire shape and the two legacy decoding modes are checked without a simulator.
payload=[1,7,None,{'ascii_key':[1.25,-2,True]}]
packed=msgpack.Packer(use_bin_type=False).pack(payload)
assert msgpack.unpackb(packed,raw=False)==payload
assert msgpack.unpackb(packed,raw=True)[3][b'ascii_key']==payload[3]['ascii_key']
assert msgpack.Packer.__module__=='msgpack._cmsgpack'
(record/'compatibility.json').write_text(json.dumps({'msgpack_version':msgpack.version,'backend':msgpack.Packer.__module__,'rpc_transport_before_sha256':hashlib.sha256(before.encode()).hexdigest(),'rpc_transport_after_sha256':hashlib.sha256(after.encode()).hexdigest(),'encoding':'Packer retains legacy use_bin_type=False; Unpacker raw=True only when legacy encoding was None, raw=False for UTF-8; no method/action changes','roundtrip_checks':'passed'},indent=2)+'\n')
print(record)
