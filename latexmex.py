import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, LoggingEventHandler
import subprocess
import hashlib
import os
from collections import defaultdict

def latex_hash(key):
     return hashlib.md5(open(key, "rb").read()).hexdigest()

FNULL = open(os.devnull, "w")

class LatexHandler(FileSystemEventHandler):
    def __init__(self):
        self.files = defaultdict(str)
        self.counts = defaultdict(int)
    def on_modified(self, event):
        file = os.path.basename(os.path.normpath(event.src_path))
        curr_hash = latex_hash(file)
        if file[-4:] == ".tex" and self.files[file] != curr_hash:
            print("[ Recompiling {} ({}) ]".format(file, self.counts[file]))
            self.files[file] = curr_hash
            subprocess.run("texify {}".format(file), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.run("dvipdfm {}.dvi".format(file[:-4]), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
            self.counts[file] += 1

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    event_handler = LatexHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print("[ Latex Debugging Mode ]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[ Quitting ]")
        observer.stop()
    observer.join()
