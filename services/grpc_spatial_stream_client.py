from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

import grpc

from proto_gen import spatial_stream_pb2 as pb2
from proto_gen import spatial_stream_pb2_grpc as pb2_grpc

FrameHandler = Callable[[pb2.VoxelMatrixFrame], Awaitable[None] | None]


async def stream_frames(
    cert_dir: str = "build/certs",
    target: str = "localhost:50051",
    on_frame: FrameHandler | None = None,
) -> None:
    directory = Path(cert_dir)
    credentials = grpc.ssl_channel_credentials(
        root_certificates=(directory / "root_ca.crt").read_bytes(),
        private_key=(directory / "client.key").read_bytes(),
        certificate_chain=(directory / "client.crt").read_bytes(),
    )
    async with grpc.aio.secure_channel(target, credentials) as channel:
        stub = pb2_grpc.SpatialSynthesisStreamerStub(channel)
        request = pb2.MatrixStreamRequest(
            project_node_id="configured-project-node",
            target_zoom_level=15,
            requested_pki_signature_validation=True,
        )
        async for frame in stub.StreamHydraulicVoxelMatrix(request):
            if on_frame is None:
                continue
            result = on_frame(frame)
            if result is not None:
                await result


if __name__ == "__main__":
    asyncio.run(stream_frames())
