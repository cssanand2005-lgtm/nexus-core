import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from models import TelemetryData, DeviceStatus

class ProcessingEngine:
    def __init__(self, output_queue: queue.Queue, max_workers: int = 2):
        self.output_queue = output_queue
        self._lock = threading.Lock()
        self._max_workers = max_workers
        self._observers = []  # List of registered observers for the Observer Pattern

    def add_observer(self, observer):
        """Registers a new observer to receive event notifications"""
        with self._lock:
            self._observers.append(observer)

    def _notify_observers(self, data: TelemetryData):
        """Notifies all registered observers of a state change"""
        for observer in self._observers:
            observer.update(data)

    def process_payload(self, data: TelemetryData):
        """Thread-safe single payload processing with business rules & notifications"""
        with self._lock:
            if data.temperature > 90.0:
                data.status = DeviceStatus.CRITICAL
                # Trigger Observer notification
                self._notify_observers(data)
            else:
                data.status = DeviceStatus.ACTIVE
                
            self.output_queue.put(data)

    def process_batch(self, payloads: list[TelemetryData]):
        """Processes a batch of payloads concurrently using a ThreadPoolExecutor"""
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            executor.map(self.process_payload, payloads)