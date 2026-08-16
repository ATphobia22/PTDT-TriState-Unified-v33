from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import AsyncIterator, Callable
from pathlib import Path

import grpc

from proto_gen import spatial_stream_pb2 as pb2
from proto_gen import spatial_stream_pb2_grpc as pb2_grpc

FrameProvider = Callable[[int, str], tuple[float, tuple[float, float, float], bytes, str]]


class SpatialStreamerService(pb2_grpc.SpatialSynthesisStreamerServicer):
    def __init__(self, frame_provider: FrameProvider) -> None:
        self.frame_provider = frame_provider

    async def StreamHydraulicVoxelMatrix(
        self, request: pb2.MatrixStreamRequest, context: grpc.aio.ServicerContext
    ) -> AsyncIterator[pb2.VoxelMatrixFrame]:
        if not request.project_node_id:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "project_node_id is required")
        if request.target_zoom_level > 30:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "target_zoom_level must be <= 30")

        timestep = 0
        interval = 1.0 / 30.0
        next_tick = time.monotonic()
        while context.is_active():
            wse, ecef, payload, digest = self.frame_provider(timestep, request.project_node_id)
            if hashlib.sha256(payload).hexdigest() != digest:
                await context.abort(grpc.StatusCode.DATA_LOSS, "frame evidence hash mismatch")
            yield pb2.VoxelMatrixFrame(
                timestamp_epoch_ms=int(time.time() * 1000),
                timestep_index=timestep,
                calculated_wse_navd88_ft=wse,
                geocentric_anchor_epsg4978=pb2.CoordinateECEF(x=ecef[0], y=ecef[1], z=ecef[2]),
                evidence_sha256=digest,
                depth_voxels_float32_le=payload,
            )
            timestep += 1
            next_tick += interval
            await asyncio.sleep(max(0.0, next_tick - time.monotonic()))

    async def VerifyLedgerNodeIntegrity(
        self, request: pb2.LedgerVerificationRequest, context: grpc.aio.ServicerContext
    ) -> pb2.LedgerVerificationResponse:
        if not request.target_node_id or not request.declared_evidence_hash:
            return pb2.LedgerVerificationResponse(
                is_immutable_chain_valid=False,
                verification_message="node id and declared evidence hash are required",
            )
        return pb2.LedgerVerificationResponse(
            is_immutable_chain_valid=False,
            verification_message="verification requires an injected evidence-registry provider",
        )


def load_server_credentials(cert_dir: str | Path) -> grpc.ServerCredentials:
    directory = Path(cert_dir)
    private_key = (directory / "server.key").read_bytes()
    certificate_chain = (directory / "server.crt").read_bytes()
    root_ca = (directory / "root_ca.crt").read_bytes()
    return grpc.ssl_server_credentials(
        [(private_key, certificate_chain)],
        root_certificates=root_ca,
        require_client_auth=True,
    )


async def serve(service: SpatialStreamerService, cert_dir: str | Path, listen_addr: str = "[::]:50051") -> None:
    server = grpc.aio.server(options=[
        ("grpc.max_send_message_length", 16 * 1024 * 1024),
        ("grpc.max_receive_message_length", 1 * 1024 * 1024),
    ])
    pb2_grpc.add_SpatialSynthesisStreamerServicer_to_server(service, server)
    server.add_secure_port(listen_addr, load_server_credentials(cert_dir))
    await server.start()
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=5)
