import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from google.cloud import logging as cloud_logging

def setup_logging():
    """Initialize Google Cloud Logging"""
    try:
        client = cloud_logging.Client()
        client.setup_logging()
    except Exception as e:
        print(f"Warning: Could not initialize Cloud Logging: {e}")
        logging.basicConfig(level=logging.INFO)
    
    return logging.getLogger(__name__)

def setup_tracing():
    """Initialize OpenTelemetry tracing with Cloud Trace"""
    project_id = os.getenv("GCP_PROJECT_ID", "")
    resource = Resource.create({"service.name": "library-api"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    if project_id:
        try:
            cloud_trace_exporter = CloudTraceSpanExporter(project_id=project_id)
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(cloud_trace_exporter)
            )
        except Exception as e:
            logging.warning(f"Could not initialize Cloud Trace: {e}")
    
    return tracer

logger = setup_logging()
tracer = setup_tracing()