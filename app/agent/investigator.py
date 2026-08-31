class InvestigationAgent:
    """AI agent for generating investigation summaries based on structured evidence."""
    
    @staticmethod
    def generate_railway_investigation(evidence):
        """Generate investigation summary for railway risk."""
        animal = evidence.get('animal')
        distance_m = evidence.get('railway_distance_m', 0)
        eta_min = evidence.get('railway_eta_min')
        moving_toward = evidence.get('moving_toward_railway', False)
        cctv_confirmed = evidence.get('cctv_confirmed', False)
        anomaly = evidence.get('movement_anomaly', False)
        risk_score = evidence.get('risk_score', 0)
        
        summary = f"CRITICAL RAILWAY WILDLIFE RISK\n\n"
        
        if animal and animal.get('species'):
            summary += f"{animal['species'].upper()} {animal.get('animal_code', 'UNKNOWN')} is "
        else:
            summary += "Animal is "
        
        if moving_toward:
            summary += "moving toward the railway corridor "
        else:
            summary += "in proximity to the railway corridor "
        
        summary += f"and is approximately {distance_m} metres away.\n\n"
        
        if eta_min:
            summary += f"Current trajectory indicates an estimated approach time of approximately {eta_min} minutes.\n\n"
        
        if cctv_confirmed:
            summary += "CCTV independently confirms the animal's presence.\n\n"
        
        if anomaly:
            summary += "Movement anomaly detected - animal is behaving unusually.\n\n"
        
        summary += f"Risk Score: {risk_score}/100\n\n"
        
        summary += "Recommended action:\n\n"
        summary += "Immediate field verification and coordination with the appropriate forest and railway control personnel.\n\n"
        
        summary += "Action Items:\n"
        summary += "1. Deploy field team to verify animal location and behavior\n"
        summary += "2. Notify railway control center for precautions\n"
        summary += "3. Monitor animal movement in real-time\n"
        summary += "4. Prepare tranquilization if necessary\n"
        
        return summary
    
    @staticmethod
    def generate_village_investigation(evidence):
        """Generate investigation summary for village conflict risk."""
        animal = evidence.get('animal')
        distance_m = evidence.get('village_distance_m', 0)
        eta_min = evidence.get('village_eta_min')
        moving_toward = evidence.get('moving_toward_village', False)
        cctv_confirmed = evidence.get('cctv_confirmed', False)
        anomaly = evidence.get('movement_anomaly', False)
        risk_score = evidence.get('risk_score', 0)
        village_name = evidence.get('village_name', 'Unknown')
        
        summary = f"POTENTIAL HUMAN-WILDLIFE CONFLICT\n\n"
        
        if animal and animal.get('species'):
            summary += f"{animal['species'].upper()} {animal.get('animal_code', 'UNKNOWN')} is "
        else:
            summary += "Animal is "
        
        if moving_toward:
            summary += f"approaching {village_name} "
        else:
            summary += f"in proximity to {village_name} "
        
        summary += f"and is approximately {distance_m} metres away.\n\n"
        
        if eta_min:
            summary += f"Current trajectory indicates an estimated approach time of approximately {eta_min} minutes.\n\n"
        
        if cctv_confirmed:
            summary += "CCTV independently confirms the animal's presence.\n\n"
        
        if anomaly:
            summary += "Movement anomaly detected - animal is behaving unusually.\n\n"
        
        summary += f"Risk Score: {risk_score}/100\n\n"
        
        summary += "Recommended action:\n\n"
        summary += "Immediate field verification and coordination with village authorities to mitigate human-wildlife conflict.\n\n"
        
        summary += "Action Items:\n"
        summary += "1. Notify village authorities for community safety measures\n"
        summary += "2. Deploy field team to monitor animal behavior\n"
        summary += "3. Establish exclusion zones if necessary\n"
        summary += "4. Prepare for capture/relocation if animal enters village\n"
        
        return summary
    
    @staticmethod
    def generate_investigation(threat_type, evidence):
        """Generate investigation summary based on threat type."""
        if threat_type == 'railway':
            return InvestigationAgent.generate_railway_investigation(evidence)
        elif threat_type == 'village':
            return InvestigationAgent.generate_village_investigation(evidence)
        else:
            return "Unable to generate investigation summary - unknown threat type."
