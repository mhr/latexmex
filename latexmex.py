import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import hashlib
import os
import glob
from collections import defaultdict

def latex_hash(key):
     return hashlib.md5(open(key, "rb").read()).hexdigest()

FNULL = open(os.devnull, "w")

class LatexHandler(FileSystemEventHandler):
    def __init__(self):
        self.texfiles = defaultdict(str)
        self.counts = defaultdict(int)
    def on_modified(self, event):
        texfile = os.path.basename(os.path.normpath(event.src_path))
        if texfile.endswith(".tex"):
            curr_hash = latex_hash(texfile)
            if self.texfiles[texfile] != curr_hash:
                print("[ Recompiling {} ({}) ]".format(texfile, self.counts[texfile]))
                self.texfiles[texfile] = curr_hash
                subprocess.run("texify {}".format(texfile), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                subprocess.run("dvipdfm {}.dvi".format(texfile[:-4]), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                self.cleanup()
                self.counts[texfile] += 1
    def cleanup(self):
        for f in glob.glob("*.log"):
            os.remove(f)
        for f in glob.glob("*.dvi"):
            os.remove(f)
        for f in glob.glob("*.aux"):
            os.remove(f)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    event_handler = LatexHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print("[ LaTeXMeX Debugging Mode ]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[ Quitting ]")
        observer.stop()
    observer.join()
