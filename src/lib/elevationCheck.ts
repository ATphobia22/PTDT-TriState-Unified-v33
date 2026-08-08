export interface StageResult {
  stage_ft: number;
  bfe_ft: number;
  freeboard_ft: number;
  above_bfe: boolean;
  datum: string;
}

const BFE = 375.0;
const LAG = 377.2;

export function stageVsBfe(stageFt: number): StageResult {
  const freeboard = stageFt - BFE;
  return {
    stage_ft: stageFt,
    bfe_ft: BFE,
    freeboard_ft: freeboard,
    above_bfe: freeboard > 0,
    datum: 'NAVD88',
  };
}

export function compensatoryStorage(fillCy: number, surchargeFt = 0.0) {
  const required = fillCy * 1.20;
  return {
    fill_cy: fillCy,
    required_compensatory_cy: required,
    surcharge_ft: surchargeFt,
    bfe_ft_navd88: BFE,
    passed: surchargeFt <= 0.0 && required >= fillCy,
    datum: 'NAVD88',
    rule: 'IN-312-IAC-10',
  };
}

export const SITE = {
  address: '13101 Bonebank Road, Section 35, Posey County, IN',
  bfe_ft: BFE,
  lag_ft: LAG,
  berm_crest_ft: 379.8,
};
