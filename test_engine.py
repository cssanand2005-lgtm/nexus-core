import queue
from engine import ProcessingEngine
from models import TelemetryData, DeviceStatus

class MockAlertObserver:
    def __init__(self):
        self.alerts = []

    def update(self, data: TelemetryData):
        if data.status == DeviceStatus.CRITICAL:
            self.alerts.append(data)

def test_engine_processing():
    output_queue = queue.Queue()
    engine = ProcessingEngine(output_queue=output_queue)
    
    sample_data = TelemetryData("sensor_02", 95.0, DeviceStatus.WARNING)
    engine.process_payload(sample_data)
    
    result = output_queue.get(timeout=1)
    assert result.device_id == "sensor_02"
    assert result.status == DeviceStatus.CRITICAL

def test_concurrent_batch_processing():
    output_queue = queue.Queue()
    engine = ProcessingEngine(output_queue=output_queue, max_workers=4)
    
    payloads = [
        TelemetryData(f"sensor_0{i}", 60.0 + (i * 10), DeviceStatus.ACTIVE)
        for i in range(1, 6)
    ]
    
    engine.process_batch(payloads)
    
    results = []
    while not output_queue.empty():
        results.append(output_queue.get(timeout=1))
        
    assert len(results) == 5
    critical_sensors = [r for r in results if r.status == DeviceStatus.CRITICAL]
    assert len(critical_sensors) == 2

def test_observer_pattern_alerts():
    """Test that registered observers receive critical event notifications"""
    output_queue = queue.Queue()
    engine = ProcessingEngine(output_queue=output_queue)
    
    # Register our mock observer
    observer = MockAlertObserver()
    engine.add_observer(observer)
    
    # Process a critical payload
    critical_data = TelemetryData("reactor_01", 105.0, DeviceStatus.ACTIVE)
    engine.process_payload(critical_data)
    
    # Verify observer caught the critical alert
    assert len(observer.alerts) == 1
    assert observer.alerts[0].device_id == "reactor_01"

if __name__ == "__main__":
    test_engine_processing()
    test_concurrent_batch_processing()
    test_observer_pattern_alerts()