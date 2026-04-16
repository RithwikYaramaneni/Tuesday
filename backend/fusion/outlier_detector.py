from typing import List
import numpy as np
from haversine import haversine, Unit
from models import LocationPoint

def detect_outliers(points: List[LocationPoint]) -> List[LocationPoint]:
    """
    Calculates the spatial median of incoming signals.
    Calculates the Haversine distance from every point to the median.
    Flags points > 2km away as outliers and filters them out of the returned list.
    """
    # If there are 2 or fewer points, an outlier cluster doesn't mathematically make sense
    if len(points) <= 2:
        return points

    # 1. Find the spatial median (center point of the cluster)
    latitudes = [p.latitude for p in points]
    longitudes = [p.longitude for p in points]
    
    median_lat = np.median(latitudes)
    median_lon = np.median(longitudes)
    
    median_coord = (median_lat, median_lon)
    
    valid_points = []
    
    # 2. Calculate distance and filter exactly as per instructions
    for point in points:
        point_coord = (point.latitude, point.longitude)
        
        # Haversine distance in Kilometers
        distance_km = haversine(point_coord, median_coord, unit=Unit.KILOMETERS)
        
        if distance_km > 2.0:
            # Flag it
            point.is_outlier = True
            point.outlier_reason = f"Distance to cluster median is {distance_km:.2f} km (Limit: 2 km)"
            # It is excluded from the valid list
        else:
            valid_points.append(point)
            
    return valid_points
