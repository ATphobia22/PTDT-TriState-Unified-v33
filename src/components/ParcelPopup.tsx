import React, { useEffect, useState } from "react";

export interface ProxyParcelDetail {
  status: "OK" | "SOFT_FAIL" | string;
  parcel_id: string;
  source_url?: string;
  property_address?: string | null;
  city?: string | null;
  state?: string | null;
  zip?: string | null;
  owner_name?: string | null;
  legal_description?: string | null;
  property_class?: string | null;
  total_acreage?: number | null;
  land_value_latest?: number | null;
  improvement_value_latest?: number | null;
  total_value_latest?: number | null;
  assessment_year_latest?: number | null;
  reason?: string | null;
}

interface ParcelPopupProps {
  parcelId: string;
  onClose: () => void;
  /** Default local FastAPI */
  apiBase?: string;
}

const money = (n: number | null | undefined) =>
  n == null
    ? "—"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(n);

/** Presentation-only — routes through server proxy (no browser→Engage CORS). */
export const ParcelPopup: React.FC<ParcelPopupProps> = ({
  parcelId,
  onClose,
  apiBase = "",
}) => {
  const [data, setData] = useState<ProxyParcelDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    const url = `${apiBase}/api/proxy/xsoft/posey/parcel?parcel_id=${encodeURIComponent(parcelId)}`;
    fetch(url)
      .then(async (res) => {
        if (!res.ok) throw new Error(`proxy HTTP ${res.status}`);
        return (await res.json()) as ProxyParcelDetail;
      })
      .then((result) => {
        if (mounted) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (mounted) {
          setData({
            status: "SOFT_FAIL",
            parcel_id: parcelId,
            reason: err instanceof Error ? err.message : "proxy unreachable",
          });
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [parcelId, apiBase]);

  return (
    <div
      style={{
        fontFamily: "monospace",
        padding: 12,
        color: "#00ff66",
        backgroundColor: "rgba(10,15,24,0.9)",
        border: "1px solid #00ff66",
        borderRadius: 4,
        maxWidth: 320,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span style={{ color: "#fff", fontWeight: "bold" }}>APN PROXY</span>
        <button
          type="button"
          onClick={onClose}
          style={{
            background: "none",
            border: "none",
            color: "#ff3333",
            cursor: "pointer",
          }}
        >
          [X]
        </button>
      </div>
      <div style={{ fontSize: 11, marginTop: 8 }}>
        <span style={{ color: "#888" }}>PARCEL:</span> {parcelId}
      </div>
      {loading && <div style={{ marginTop: 8 }}>QUERYING LOCAL PROXY...</div>}
      {!loading && data?.status === "SOFT_FAIL" && (
        <div style={{ marginTop: 8, color: "#ff6666", fontSize: 11 }}>
          SOFT_FAIL: {data.reason}
          {data.source_url && (
            <div style={{ marginTop: 6 }}>
              <a
                href={data.source_url}
                target="_blank"
                rel="noreferrer"
                style={{ color: "#88ffcc" }}
              >
                Open Engage
              </a>
            </div>
          )}
        </div>
      )}
      {!loading && data?.status === "OK" && (
        <div style={{ marginTop: 8, fontSize: 11, display: "grid", gap: 4 }}>
          <div>OWNER: {data.owner_name ?? "—"}</div>
          <div>SITUS: {data.property_address ?? "—"}</div>
          <div>
            {data.city} {data.state} {data.zip}
          </div>
          <div>CLASS: {data.property_class ?? "—"}</div>
          <div>ACRES: {data.total_acreage ?? "—"}</div>
          <div>
            LAND {money(data.land_value_latest)} | IMP{" "}
            {money(data.improvement_value_latest)}
          </div>
          <div style={{ fontWeight: "bold" }}>
            TOTAL {money(data.total_value_latest)} ({data.assessment_year_latest})
          </div>
          {data.source_url && (
            <a
              href={data.source_url}
              target="_blank"
              rel="noreferrer"
              style={{ color: "#88ffcc" }}
            >
              Official detail
            </a>
          )}
        </div>
      )}
    </div>
  );
};
