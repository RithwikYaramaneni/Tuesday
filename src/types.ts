export interface LocationPoint {
  signal_id: string;
  latitude: number;
  longitude: number;
  source: string;
  accuracy_radius_m: number;
  raw_confidence: number;
  is_outlier: boolean;
  outlier_reason: string | null;
}

export interface FusedLocation {
  fused_lat: number;
  fused_lon: number;
  confidence_score: number;
  uncertainty_radius_m: number;
  dispatch_status: 'GREEN' | 'YELLOW' | 'RED';
  sources_used: string[];
  sources_ignored: string[];
  explanation: string;
  followup_question: string | null;
  input_signals: LocationPoint[];
}
