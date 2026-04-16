import type { FusedLocation } from './types';

export const mockGreenScenario: FusedLocation = {
  fused_lat: 13.0827,
  fused_lon: 80.2707,
  confidence_score: 95,
  uncertainty_radius_m: 15,
  dispatch_status: 'GREEN',
  sources_used: ['cell', 'gps', 'w3w'],
  sources_ignored: [],
  explanation: 'High confidence location lock. GPS, What3Words, and Cell Tower triangulation all resolved to the exact same 15-meter radius.',
  followup_question: null,
  input_signals: [
    { signal_id: 'sig-1', latitude: 13.0828, longitude: 80.2706, source: 'gps', accuracy_radius_m: 10, raw_confidence: 98, is_outlier: false, outlier_reason: null },
    { signal_id: 'sig-2', latitude: 13.0825, longitude: 80.2709, source: 'w3w', accuracy_radius_m: 3, raw_confidence: 100, is_outlier: false, outlier_reason: null },
    { signal_id: 'sig-3', latitude: 13.0830, longitude: 80.2700, source: 'cell', accuracy_radius_m: 200, raw_confidence: 70, is_outlier: false, outlier_reason: null }
  ]
};

export const mockYellowScenario: FusedLocation = {
  fused_lat: 13.0450,
  fused_lon: 80.2250,
  confidence_score: 55,
  uncertainty_radius_m: 250,
  dispatch_status: 'YELLOW',
  sources_used: ['cell', 'wifi'],
  sources_ignored: ['gps'],
  explanation: 'Signal conflict detected. The GPS ping is highly stale and places the caller across the city from the active Cell and Wi-Fi networks.',
  followup_question: 'Are you currently near the large grocery store on 4th Avenue?',
  input_signals: [
    { signal_id: 'sig-4', latitude: 13.0450, longitude: 80.2250, source: 'cell', accuracy_radius_m: 500, raw_confidence: 65, is_outlier: false, outlier_reason: null },
    { signal_id: 'sig-5', latitude: 13.0448, longitude: 80.2252, source: 'wifi', accuracy_radius_m: 50, raw_confidence: 80, is_outlier: false, outlier_reason: null },
    { signal_id: 'sig-6', latitude: 12.9000, longitude: 80.1500, source: 'gps', accuracy_radius_m: 20, raw_confidence: 10, is_outlier: true, outlier_reason: 'Timestamp is over 4 hours old. Rejected.' }
  ]
};

export const mockRedScenario: FusedLocation = {
  fused_lat: 13.0100,
  fused_lon: 80.2000,
  confidence_score: 18,
  uncertainty_radius_m: 3500,
  dispatch_status: 'RED',
  sources_used: ['ip_geo'],
  sources_ignored: ['address'],
  explanation: 'High uncertainty. We only have weak IP geolocation data. The provided address string could not be definitively validated against the municipal geodatabase.',
  followup_question: 'We cannot get a geo-lock on your device. Please describe what you see nearby or read a nearby street sign.',
  input_signals: [
    { signal_id: 'sig-7', latitude: 13.0100, longitude: 80.2000, source: 'ip_geo', accuracy_radius_m: 5000, raw_confidence: 30, is_outlier: false, outlier_reason: null },
    { signal_id: 'sig-8', latitude: 0, longitude: 0, source: 'address', accuracy_radius_m: 0, raw_confidence: 0, is_outlier: true, outlier_reason: 'Address string parsed to 0 matching hits.' }
  ]
};

export const ALL_SCENARIOS = [mockGreenScenario, mockYellowScenario, mockRedScenario];
