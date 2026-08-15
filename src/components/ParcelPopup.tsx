import React, { useEffect, useState } from "react";
import {
  fetchXSoftParcelData,
  type XSoftParcelDetail,
} from "../services/xsoftService";

interface ParcelPopupProps {
  parcelId: string;
  onClose: () => void;
}

/** Presentation-only APN probe. Does not set LOMA eligibility. */
export const ParcelPopup: React.FC<ParcelPopupProps> = ({ parcelId, onClose }) => {
  const [data, setData] = useState<XSoftParcelDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchXSoftParcelData(parcelId).then((result) => {
      if (mounted) {
        setData(result);
        setLoading(false);
      }
    });
    return () => {
      mounted = false;
    };
  }, [parcelId]);

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
        <span style={{ color: "#fff", fontWeight: "bold" }}>APN PROBE (XSoft)</span>
        <button
          type="button"
          onClick={onClose}
          style={{ background: "none", border: "none", color: "#ff3333", cursor: "pointer" }}
        >
          [X]
        </button>
      </div>
      <div style={{ fontSize: 11, marginTop: 8 }}>
        <span style={{ color: "#888" }}>PARCEL:</span> {parcelId}
      </div>
      {loading && <div style={{ marginTop: 8 }}>QUERYING ENGAGE...</div>}
      {!loading && data?.status === "SOFT_FAIL" && (
        <div style={{ marginTop: 8, color: "#ff6666", fontSize: 11 }}>
          SOFT_FAIL: {data.reason}
          <div style={{ marginTop: 6 }}>
            <a href={data.sourceUrl} target="_blank" rel="noreferrer" style={{ color: "#88ffcc" }}>
              Open Posey Engage
            </a>
          </div>
        </div>
      )}
      {!loading && data?.status === "OK" && (
        <div style={{ marginTop: 8, fontSize: 11 }}>
          <div>content-type: {data.contentType || "(none)"}</div>
          <div>html: {String(data.htmlDocument)}</div>
          <div style={{ marginTop: 6 }}>
            <a href={data.sourceUrl} target="_blank" rel="noreferrer" style={{ color: "#88ffcc" }}>
              Open official detail
            </a>
          </div>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 9, maxHeight: 120, overflow: "auto" }}>
            {data.rawPreview.slice(0, 400)}
          </pre>
        </div>
      )}
    </div>
  );
};
