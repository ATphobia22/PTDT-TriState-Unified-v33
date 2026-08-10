import React from 'react';

interface ForensicHUDProps {
  stageFt: number;
  depthM: number;
  dischargeCfs: number;
  fos: number;
  station: string;
  timestamp: string;
  alert: boolean;
}

export function ForensicHUD({
  stageFt,
  depthM,
  dischargeCfs,
  fos,
  station,
  timestamp,
  alert,
}: ForensicHUDProps) {
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        right: 16,
        display: 'flex',
        gap: 12,
        flexWrap: 'wrap',
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        fontSize: 12,
        color: '#e0f2fe',
        pointerEvents: 'none',
      }}
    >
      <Badge label="STATION" value={station} />
      <Badge label="STAGE" value={`${stageFt.toFixed(2)} ft`} />
      <Badge label="DEPTH" value={`${depthM.toFixed(2)} m`} />
      <Badge label="Q" value={`${Math.round(dischargeCfs).toLocaleString()} cfs`} />
      <Badge
        label="FoS"
        value={fos.toFixed(2)}
        warn={fos < 1.4}
      />
      <Badge label="UTC" value={timestamp} />
      {alert && (
        <div
          style={{
            background: 'rgba(185,28,28,0.9)',
            padding: '6px 10px',
            borderRadius: 6,
            border: '1px solid #f87171',
            fontWeight: 700,
          }}
        >
          THRESHOLD BREACH — FEMA MT-2 DOSSIER ARMED
        </div>
      )}
    </div>
  );
}

function Badge({
  label,
  value,
  warn,
}: {
  label: string;
  value: string;
  warn?: boolean;
}) {
  return (
    <div
      style={{
        background: warn ? 'rgba(127,29,29,0.85)' : 'rgba(8,16,28,0.88)',
        padding: '6px 10px',
        borderRadius: 6,
        border: `1px solid ${warn ? '#f87171' : 'rgba(56,189,248,0.25)'}`,
        backdropFilter: 'blur(8px)',
      }}
    >
      <span style={{ opacity: 0.6, marginRight: 6 }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  );
}
