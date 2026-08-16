from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Mapping

import rfc8785
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


class FemaAppealPackager:
    """Generate an engineering evidence dossier; not an agency submission gateway."""

    def __init__(self, workspace_root: str = "build") -> None:
        self.root = Path(workspace_root)
        self.staging_dir = self.root / "evidence_dossier_staging"
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _render_pdf(self, output_path: Path, metrics: Mapping[str, Any], seal: str) -> None:
        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        body = styles["BodyText"]
        story = [
            Paragraph("PTDT ENGINEERING CLEARANCE EVIDENCE DOSSIER", styles["Title"]),
            Paragraph(datetime.now(timezone.utc).isoformat(), body),
            Spacer(1, 12),
        ]
        rows = [["Parameter", "Value"]]
        for key in (
            "building_id", "structural_use", "lowest_adjacent_grade_ft",
            "first_floor_elevation_ft", "current_water_surface_ft",
            "lowest_floor_freeboard_ft", "hydrostatic_threat_status",
            "statutory_compliance_pass",
        ):
            rows.append([key, str(metrics.get(key, ""))])
        table = Table(rows, colWidths=[220, 280], repeatRows=1)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, "#94a3b8"),
            ("BACKGROUND", (0, 0), (-1, 0), "#e2e8f0"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([table, Spacer(1, 12), Paragraph(f"Manifest SHA-256: {seal}", body)])
        document.build(story)

    def compile_fema_appeal_package(self, clearance_manifest: Mapping[str, Any]) -> Path | None:
        metrics = clearance_manifest.get("compliance_metrics", clearance_manifest)
        if bool(metrics.get("statutory_compliance_pass", True)):
            return None
        building_id = str(metrics.get("building_id", "unknown-node")).replace("/", "_")
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        for path in self.staging_dir.iterdir():
            if path.is_file():
                path.unlink()

        manifest_bytes = rfc8785.dumps(dict(clearance_manifest))
        manifest_path = self.staging_dir / "structural_clearance_manifest.json"
        manifest_path.write_bytes(manifest_bytes)
        manifest_seal = self._sha256_bytes(manifest_bytes)

        pdf_path = self.staging_dir / "engineering_clearance_brief.pdf"
        self._render_pdf(pdf_path, metrics, manifest_seal)
        pdf_seal = self._sha256_bytes(pdf_path.read_bytes())

        package_manifest = {
            "dossier_type": "PTDT_ENGINEERING_CLEARANCE_EVIDENCE",
            "compiled_utc": datetime.now(timezone.utc).isoformat(),
            "regulatory_submission_status": "NOT_SUBMITTED",
            "components": [
                {"file": manifest_path.name, "sha256": manifest_seal},
                {"file": pdf_path.name, "sha256": pdf_seal},
            ],
        }
        package_path = self.staging_dir / "package_manifest.json"
        package_path.write_bytes(rfc8785.dumps(package_manifest))

        archive = self.root / f"FEMA_HMA_APPEAL_DOSSIER_NODE_{building_id}.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for path in sorted(self.staging_dir.iterdir()):
                tar.add(path, arcname=f"appeal_dossier/{path.name}")
        return archive
