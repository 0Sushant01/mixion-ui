"""
Pour Engine
Business logic for converting ml to seconds and sending MQTT commands
"""


class PourEngine:
    """Handles drink dispensing logic"""
    
    def __init__(self, database, mqtt_client):
        """
        Initialize pour engine
        
        Args:
            database: Database instance
            mqtt_client: MQTTClient instance
        """
        self.db = database
        self.mqtt = mqtt_client
    
    def dispense_drink(self, drink_id):
        """
        Dispense a predefined drink
        
        Args:
            drink_id: ID of the drink to dispense
        
        Returns:
            tuple: (success: bool, message: str, msg_id: str or None)
        """
        try:
            # Get recipe for the drink
            recipes = self.db.get_recipes_for_drink(drink_id)
            
            if not recipes:
                return False, "No recipe found for this drink", None, None
            
            # Build jobs from recipes
            jobs = []
            for recipe in recipes:
                duration_sec = self._calculate_duration(
                    recipe['amount_ml'],
                    recipe['flow_rate']
                )
                
                jobs.append({
                    "relay": recipe['bottle_id'],
                    "amount_ml": recipe['amount_ml'],
                    "duration_sec": duration_sec
                })
            
            # Send MQTT command
            success, msg_id, payload = self.mqtt.publish_dispense_command(jobs)
            
            if success:
                return True, "Dispense command sent successfully", msg_id, payload
            else:
                return False, "Failed to send MQTT command", None, payload
                
        except Exception as e:
            return False, f"Error dispensing drink: {str(e)}", None, None
    
    def dispense_custom(self, bottle_amounts):
        """
        Dispense custom mix
        
        Args:
            bottle_amounts: Dict mapping bottle_id to amount_ml
                           Example: {1: 50, 2: 75, 3: 25}
        
        Returns:
            tuple: (success: bool, message: str, msg_id: str or None)
        """
        try:
            # Validate limits
            limits_map = self.db.get_limits_map()
            
            for bottle_id, amount_ml in bottle_amounts.items():
                if bottle_id in limits_map:
                    limits = limits_map[bottle_id]
                    if amount_ml < limits['min_ml']:
                        return False, f"Amount too low for bottle {bottle_id}", None
                    if amount_ml > limits['max_ml']:
                        return False, f"Amount too high for bottle {bottle_id}", None
            
            # Build jobs
            jobs = []
            for bottle_id, amount_ml in bottle_amounts.items():
                if amount_ml <= 0:
                    continue
                
                bottle = self.db.get_bottle_by_id(bottle_id)
                if not bottle:
                    return False, f"Bottle {bottle_id} not found", None
                
                if not bottle['enabled']:
                    return False, f"Bottle {bottle['name']} is disabled", None
                
                duration_sec = self._calculate_duration(
                    amount_ml,
                    bottle['flow_rate']
                )
                
                jobs.append({
                    "relay": bottle['id'],
                    "amount_ml": amount_ml,
                    "duration_sec": duration_sec
                })
            
            if not jobs:
                return False, "No valid bottles selected", None
            
            # Send MQTT command
            success, msg_id, payload = self.mqtt.publish_dispense_command(jobs)
            
            if success:
                return True, "Custom dispense command sent successfully", msg_id, payload
            else:
                return False, "Failed to send MQTT command", None, payload
                
        except Exception as e:
            return False, f"Error dispensing custom mix: {str(e)}", None, None
    
    def _calculate_duration(self, amount_ml, flow_rate):
        """
        Calculate pour duration in seconds
        
        Args:
            amount_ml: Amount to dispense in milliliters
            flow_rate: Flow rate in ml per minute (ml/min)
        
        Returns:
            float: Duration in seconds (rounded to 2 decimal places)
        
        Formula: duration_sec = (amount_ml / flow_rate_ml_min) * 60
        """
        if flow_rate <= 0:
            raise ValueError("Flow rate must be greater than 0")
        
        # Convert flow_rate from ml/min to ml/sec by dividing by 60
        # Then calculate duration: amount_ml / (flow_rate / 60) = (amount_ml * 60) / flow_rate
        duration = (amount_ml * 60) / flow_rate
        return round(duration, 2)
