#!/usr/bin/env bash
set -euo pipefail

rm -rf proto_gen
mkdir -p proto_gen
python -m grpc_tools.protoc \
  -I proto \
  --python_out=proto_gen \
  --grpc_python_out=proto_gen \
  proto/spatial_stream.proto

# Make generated imports package-local for the service modules.
python - <<'PY'
from pathlib import Path
p = Path('proto_gen/spatial_stream_pb2_grpc.py')
s = p.read_text(encoding='utf-8')
s = s.replace('import spatial_stream_pb2 as spatial__stream__pb2', 'from . import spatial_stream_pb2 as spatial__stream__pb2')
p.write_text(s, encoding='utf-8')
PY

touch proto_gen/__init__.py
