from typing import List
from models import LocationPoint

def assign_weights(points: List[LocationPoint]) -> List[LocationPoint]:
    """
    Parses the incoming LocationPoint list and assigns a confidence weight 
    to each source based on the reliability table and environmental factors.
    """
    for point in points:
        source = point.source.upper()
        # Treat None as outdoor (False) for standard conservative fallback unless strictly true
        is_indoor = point.is_indoor is True 
        
        # 1. Base weight selection from reliability table
        base_weight = 0.0
        
        if source == "GPS":
            base_weight = 0.30 if is_indoor else 0.90
        elif source == "W3W":
            base_weight = 0.85
        elif source == "WIFI":
            base_weight = 0.75
        elif source == "ADDRESS":
            base_weight = 0.70
        elif source == "CELL":
            base_weight = 0.55
        elif source == "LANDMARK":
            base_weight = 0.40
        else:
            base_weight = 0.50 # Default safe fallback
            
        # 2. Logic additions: Environmental Penalties
        penalty = 0.0
        
        # HDOP penalty for GPS (Dilution of Precision: < 2 is excellent, > 5 is poor)
        if point.hdop is not None:
            if point.hdop >= 5.0:
                penalty += 0.40
            elif point.hdop > 2.0:
                penalty += 0.15
                
        # Signal strength penalty (dBm is negative; closer to zero is stronger. < -100 is very weak)
        if point.signal_strength_dbm is not None:
            if point.signal_strength_dbm <= -110:
                penalty += 0.20
            elif point.signal_strength_dbm <= -100:
                penalty += 0.10
                
        # 3. Calculate final weight securely bounded between 0 and 1
        final_weight = max(0.0, min(1.0, base_weight - penalty))
        
        # 4. Overwrite raw_confidence with our calculated definitive weight
        point.raw_confidence = round(final_weight, 3)
        
    return points
