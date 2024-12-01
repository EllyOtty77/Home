from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
import time
import os
import sys

class RestartEventHandler(PatternMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = None
        self.restart_app()

    def on_any_event(self, event):
        self.restart_app()

    def restart_app(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, 'app.py'])

if __name__ == "__main__":
    path = "."
    event_handler = RestartEventHandler(patterns=["*.py"])
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
