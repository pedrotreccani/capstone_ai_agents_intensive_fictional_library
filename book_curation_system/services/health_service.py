import requests
from typing import Optional
from datetime import datetime
from schemas.book import HealthResponse
from config.telemetry import logger, tracer

class HealthService:
    """Service layer for health check operations"""
    
    VERSION = "1.0.0"
    
    @staticmethod
    def get_gcp_metadata(endpoint: str) -> Optional[str]:
        """Fetch metadata from GCP metadata server"""
        try:
            response = requests.get(
                f"http://metadata.google.internal/computeMetadata/v1/{endpoint}",
                headers={"Metadata-Flavor": "Google"},
                timeout=1
            )
            return response.text if response.status_code == 200 else None
        except Exception:
            return None
    
    def get_health_status(self) -> HealthResponse:
        """Get health status with system information"""
        with tracer.start_as_current_span("service_health_check"):
            region = self.get_gcp_metadata("instance/region")
            zone = self.get_gcp_metadata("instance/zone")
            
            # Extract just the zone/region name if full path is returned
            if zone and "/" in zone:
                zone = zone.split("/")[-1]
            if region and "/" in region:
                region = region.split("/")[-1]
            
            logger.info("Health check performed")
            
            return HealthResponse(
                status="healthy",
                version=self.VERSION,
                region=region,
                zone=zone,
                timestamp=datetime.utcnow()
            )