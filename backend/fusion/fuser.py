from typing import List
from models import LocationPoint, FusedLocation
from fusion.weighter import assign_weights
from fusion.outlier_detector import detect_outliers
from haversine import haversine, Unit

def fuse_locations(incoming_points: List[LocationPoint]) -> FusedLocation:
    """
    Main pipeline entry for the Fusion Engine (Person B).
    Passes points through the weighter, removes outliers, calculates 
    a weighted average, checks for consensus, and outputs the final FusedLocation.
    """
    # 1. Pipeline: Weighting and Filtering
    weighted_points = assign_weights(incoming_points)
    valid_points = detect_outliers(weighted_points)
    
    used_sources = []
    ignored_sources = []
    
    # Categorize sources for the explanation text
    for p in incoming_points:
        if p.is_outlier:
            ignored_sources.append(f"{p.source} (Outlier)")
        elif getattr(p, "raw_confidence", 0.0) <= 0.0:
            ignored_sources.append(f"{p.source} (0% Conf)")
        else:
            used_sources.append(p.source)

    if not valid_points:
        return FusedLocation(
            latitude=0.0,
            longitude=0.0,
            confidence_score=0.0,
            explanation="Failed: All incoming locations were outliers or fully unreliable.",
            uncertainty_radius_m=2000.0,
            sources_used=[],
            sources_ignored=ignored_sources,
            dispatch_status="RED"
        )

    # 2. Weighted Average Calculation
    total_weight = 0.0
    weighted_lat = 0.0
    weighted_lon = 0.0
    
    for p in valid_points:
        w = p.raw_confidence
        weighted_lat += p.latitude * w
        weighted_lon += p.longitude * w
        total_weight += w
        
    if total_weight > 0.0:
        final_lat = weighted_lat / total_weight
        final_lon = weighted_lon / total_weight
        # Base confidence is the average score of the valid sources used
        base_confidence = total_weight / len(valid_points) 
    else:
        # Fallback if weights somehow hit zero but passed through
        final_lat = sum(p.latitude for p in valid_points) / len(valid_points)
        final_lon = sum(p.longitude for p in valid_points) / len(valid_points)
        base_confidence = 0.1

    # 3. Consensus Boost (Are there ANY two independent sources within 200 meters?)
    consensus_met = False
    for i in range(len(valid_points)):
        for j in range(i + 1, len(valid_points)):
            dist_m = haversine(
                (valid_points[i].latitude, valid_points[i].longitude),
                (valid_points[j].latitude, valid_points[j].longitude),
                unit=Unit.METERS
            )
            if dist_m <= 200.0:
                consensus_met = True
                break
        if consensus_met:
            break
            
    final_confidence = base_confidence
    if consensus_met:
        # Multiply by 1.3 but strictly cap at 1.0 maximum
        final_confidence = min(1.0, final_confidence * 1.3)

    final_confidence = round(final_confidence, 3)

    # 4. Generate the Explainable Decision String
    unique_used = list(set(used_sources))
    unique_ignored = list(set(ignored_sources))
    
    if unique_ignored and unique_used:
        explanation = f"Ignored {', '.join(unique_ignored)}. Averaged {', '.join(unique_used)}."
    elif unique_used:
        explanation = f"Averaged {', '.join(unique_used)}."
        if consensus_met:
            explanation += " Sources strictly agreed."
    else:
        explanation = "Error forming explanation."

    # Map the confidence to a radius for the Dispatcher UI rings
    if final_confidence >= 0.75:
        radius_m = 40.0
        status = "GREEN"
    elif final_confidence >= 0.4:
        radius_m = 150.0
        status = "YELLOW"
    else:
        radius_m = 1000.0
        status = "RED"

    # 5. Bundle and Return
    return FusedLocation(
        latitude=round(final_lat, 6),
        longitude=round(final_lon, 6),
        confidence_score=final_confidence,
        explanation=explanation,
        uncertainty_radius_m=radius_m,
        sources_used=used_sources,
        sources_ignored=ignored_sources,
        dispatch_status=status
    )
