import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen

class WatchdogRunner(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_flask()

    def start_flask(self):
        if self.process:
            self.process.terminate()
        self.process = Popen([sys.executable, 'app.py'])

    def on_any_event(self, event):
        self.start_flask()

if __name__ == "__main__":
    path = "."
    event_handler = WatchdogRunner()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    if event_handler.process:
        event_handler.process.terminate()
