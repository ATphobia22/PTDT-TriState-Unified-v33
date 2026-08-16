from __future__ import annotations

import hashlib
import os
from pathlib import Path


def upload_evidence_package(file_path: str | Path) -> str:
    """Upload a completed dossier using explicit deployment configuration.

    This function intentionally fails closed when AWS configuration is absent.
    It does not claim that the destination is a FEMA-operated gateway.
    """
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required for S3 archival") from exc

    path = Path(file_path)
    if not path.is_file() or not path.name.startswith("FEMA_HMA_APPEAL_DOSSIER_") or path.suffixes[-2:] != [".tar", ".gz"]:
        raise ValueError("file is not a valid PTDT evidence dossier")

    bucket = os.environ.get("PTDT_EVIDENCE_BUCKET")
    region = os.environ.get("AWS_DEFAULT_REGION")
    kms_key_id = os.environ.get("PTDT_EVIDENCE_KMS_KEY_ID")
    if not bucket or not region or not kms_key_id:
        raise RuntimeError("PTDT_EVIDENCE_BUCKET, AWS_DEFAULT_REGION, and PTDT_EVIDENCE_KMS_KEY_ID are required")

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    client = boto3.client("s3", region_name=region)
    key = f"incoming/evidence/{path.name}"
    client.upload_file(
        str(path), bucket, key,
        ExtraArgs={
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": kms_key_id,
            "Metadata": {"sha256": digest, "artifact_type": "ptdt-engineering-evidence"},
        },
    )
    return digest
