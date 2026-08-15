"""
PTDT server-side XSoft Engage HTML proxy.

Canonical Posey URL (verified):
  https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId={APN}

Returns typed JSON. Soft-fail on network/parse errors.
Not regulatory authority — assessor data is presentation / reconcile aid only.
"""
from __future__ import annotations

import re
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/proxy/xsoft", tags=["xsoft-proxy"])

POSEY_DETAIL_URL = (
    "https://engage.xsoftinc.com/posey/map/getparceldetail"
)
# Forbidden: https://xsoftinc.com?parcelId=...
USER_AGENT = "PTDT-TriState-DigitalTwin/3.3 (+local-proxy; assessor-reconcile)"


class XSoftParsedParcel(BaseModel):
    status: str = Field(description="OK | SOFT_FAIL")
    parcel_id: str
    source_url: str
    property_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    owner_name: Optional[str] = None
    legal_description: Optional[str] = None
    property_class: Optional[str] = None
    township: Optional[str] = None
    taxing_district: Optional[str] = None
    school_corp: Optional[str] = None
    neighborhood: Optional[str] = None
    total_acreage: Optional[float] = None
    land_value_latest: Optional[float] = None
    improvement_value_latest: Optional[float] = None
    total_value_latest: Optional[float] = None
    assessment_year_latest: Optional[int] = None
    sales: list[dict[str, Any]] = Field(default_factory=list)
    reason: Optional[str] = None
    data_as_of: Optional[str] = None


def _money(s: str) -> Optional[float]:
    s = s.strip().replace("$", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_engage_html(html: str, parcel_id: str, source_url: str) -> XSoftParsedParcel:
    """Best-effort parse of Engage DetailPage text/HTML."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    def grab(pattern: str) -> Optional[str]:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    addr = grab(r"Property Address:\s*(.+?)\s+Neighborhood Name:")
    neighborhood = grab(r"Neighborhood Name:\s*(.+?)\s+Number\s*/\s*Factor:")
    legal = grab(r"Legal Description:\s*(.+?)\s+Property Class:")
    prop_class = grab(r"Property Class:\s*(.+?)\s+Township:")
    township = grab(r"Township:\s*(.+?)\s+Taxing District:")
    taxing = grab(r"Taxing District:\s*(.+?)\s+School Corp\.?\s*:")
    school = grab(r"School Corp\.?\s*:\s*(.+?)\s+Neighborhood Amenities")
    owner = grab(r"CURRENT OWNER\s+(.+?)\s+TRANSFER HISTORY")

    acreage: Optional[float] = None
    m_ac = re.search(r"Total Parcel Acreage\s+Land Type\s+Size\s+([0-9.]+)", text)
    if m_ac:
        try:
            acreage = float(m_ac.group(1))
        except ValueError:
            pass

    # Latest valuation row: year + Total Land + Total Improv + Total Value
    land_v = imp_v = tot_v = None
    year_v: Optional[int] = None
    m_val = re.search(
        r"(20\d{2})\s+Annual Adjustment\s+\$([0-9,.]+)\s+\$[0-9,.]+.*?"
        r"\$([0-9,.]+)\s+\$[0-9,.]+.*?\$([0-9,.]+)",
        text,
    )
    if m_val:
        year_v = int(m_val.group(1))
        land_v = _money(m_val.group(2))
        imp_v = _money(m_val.group(3))
        tot_v = _money(m_val.group(4))

    sales: list[dict[str, Any]] = []
    for sm in re.finditer(
        r"(\d{2}/\d{2}/\d{4})\s+\$([0-9,.]+)",
        text,
    ):
        sales.append({"sale_date": sm.group(1), "sale_price": _money(sm.group(2))})

    data_as_of = grab(r"Data current as of:\s*([0-9-]+)")

    city = state = zip_code = None
    if addr:
        # Heuristic: last lines often CITY / ST / ZIP in original HTML
        parts = [p.strip() for p in re.split(r"\s{2,}", addr) if p.strip()]
        if len(parts) >= 1:
            # Keep first line as street when multi-line collapsed
            pass

    m_csz = re.search(
        r"Property Address:\s*(.+?)\s+([A-Z][A-Z\s]+?)\s+(IN)\s+(\d{5})",
        text,
        re.IGNORECASE,
    )
    street = None
    if m_csz:
        street = m_csz.group(1).strip()
        city = m_csz.group(2).strip()
        state = m_csz.group(3).upper()
        zip_code = m_csz.group(4)

    return XSoftParsedParcel(
        status="OK",
        parcel_id=parcel_id,
        source_url=source_url,
        property_address=street or addr,
        city=city,
        state=state,
        zip=zip_code,
        owner_name=owner,
        legal_description=legal,
        property_class=prop_class,
        township=township,
        taxing_district=taxing,
        school_corp=school,
        neighborhood=neighborhood,
        total_acreage=acreage,
        land_value_latest=land_v,
        improvement_value_latest=imp_v,
        total_value_latest=tot_v,
        assessment_year_latest=year_v,
        sales=sales[:10],
        data_as_of=data_as_of,
    )


@router.get("/posey/parcel", response_model=XSoftParsedParcel)
async def proxy_posey_parcel(
    parcel_id: str = Query(..., min_length=5, max_length=64),
) -> XSoftParsedParcel:
    pid = parcel_id.strip()
    url = f"{POSEY_DETAIL_URL}?parcelId={pid}"
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
    except httpx.HTTPError as exc:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"network: {exc}",
        )

    if resp.status_code != 200:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"HTTP {resp.status_code}",
        )

    try:
        return parse_engage_html(resp.text, pid, url)
    except Exception as exc:  # noqa: BLE001 — soft-fail boundary
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"parse: {exc}",
        )


def mount_xsoft_proxy(app: Any) -> None:
    """Call from FastAPI app factory: mount_xsoft_proxy(app)"""
    app.include_router(router)
