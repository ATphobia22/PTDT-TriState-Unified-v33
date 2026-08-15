"""
PTDT server-side XSoft Engage HTML proxy.

Canonical Posey URL (verified):
  https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId={APN}
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("PTDT.XSoftProxy")

router = APIRouter(prefix="/api/proxy/xsoft", tags=["xsoft-proxy"])

POSEY_DETAIL_URL = "https://engage.xsoftinc.com/posey/map/getparceldetail"
USER_AGENT = "PTDT-TriState-DigitalTwin/3.3 (+local-proxy; assessor-reconcile)"
MAX_BODY_BYTES = 2_000_000
REQUEST_TIMEOUT = httpx.Timeout(20.0, connect=8.0)


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
    for sm in re.finditer(r"(\d{2}/\d{2}/\d{4})\s+\$([0-9,.]+)", text):
        sales.append({"sale_date": sm.group(1), "sale_price": _money(sm.group(2))})

    data_as_of = grab(r"Data current as of:\s*([0-9-]+)")

    city = state = zip_code = street = None
    m_csz = re.search(
        r"Property Address:\s*(.+?)\s+([A-Z][A-Z\s]+?)\s+(IN)\s+(\d{5})",
        text,
        re.IGNORECASE,
    )
    if m_csz:
        street = m_csz.group(1).strip()
        city = m_csz.group(2).strip()
        state = m_csz.group(3).upper()
        zip_code = m_csz.group(4)

    if "Parcel Number" not in text and "Parcel Identification" not in text:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=parcel_id,
            source_url=source_url,
            reason="response missing Engage parcel markers",
        )

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
    if not re.match(r"^[0-9A-Za-z.\-]+$", pid):
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url="",
            reason="invalid parcel_id charset",
        )

    url = f"{POSEY_DETAIL_URL}?parcelId={pid}"
    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
        ) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
    except httpx.TimeoutException:
        logger.warning("XSoft timeout parcel_id=%s", pid)
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason="timeout contacting Engage",
        )
    except httpx.HTTPError as exc:
        logger.warning("XSoft network error parcel_id=%s err=%s", pid, exc)
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"network: {exc}",
        )

    if resp.status_code >= 500:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"upstream 5xx HTTP {resp.status_code}",
        )
    if resp.status_code != 200:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"HTTP {resp.status_code}",
        )

    body = resp.text
    if len(body.encode("utf-8", errors="ignore")) > MAX_BODY_BYTES:
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason="response body too large",
        )

    try:
        return parse_engage_html(body, pid, url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("XSoft parse failure parcel_id=%s", pid)
        return XSoftParsedParcel(
            status="SOFT_FAIL",
            parcel_id=pid,
            source_url=url,
            reason=f"parse: {exc}",
        )


def mount_xsoft_proxy(app: Any) -> None:
    app.include_router(router)
