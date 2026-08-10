/** Live USGS NWIS hook — Station 03378500 Wabash at New Harmony */
const NWIS = 'https://waterservices.usgs.gov/nwis/iv/';

export interface UsgsReading {
  stageFt: number;
  dischargeCfs: number;
  timestamp: string;
  site: string;
}

export async function fetchWabashNewHarmony(): Promise<UsgsReading> {
  const url =
    `${NWIS}?format=json&sites=03378500&parameterCd=00065,00060&siteStatus=all`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`USGS NWIS ${res.status}`);
  const data = await res.json();

  const series = data?.value?.timeSeries ?? [];
  let stageFt = 0;
  let dischargeCfs = 0;
  let timestamp = new Date().toISOString();

  for (const s of series) {
    const code = s?.variable?.variableCode?.[0]?.value;
    const v = s?.values?.[0]?.value?.[0];
    if (!v) continue;
    timestamp = v.dateTime || timestamp;
    if (code === '00065') stageFt = parseFloat(v.value);
    if (code === '00060') dischargeCfs = parseFloat(v.value);
  }

  return {
    stageFt,
    dischargeCfs,
    timestamp,
    site: '03378500 Wabash River at New Harmony',
  };
}
