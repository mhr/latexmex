import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import hashlib
import os
import glob
from collections import defaultdict

def hash(key):
     return hashlib.md5(open(key, "rb").read()).hexdigest()

FNULL = open(os.devnull, "w")

def cleanup():
    for f in glob.glob("*.log"):
        os.remove(f)
    for f in glob.glob("*.dvi"):
        os.remove(f)
    for f in glob.glob("*.aux"):
        os.remove(f)

class LatexHandler(FileSystemEventHandler):
    def __init__(self):
        self.texfiles = defaultdict(str)
        self.counts = defaultdict(int)
    def on_modified(self, event):
        texfile = os.path.basename(os.path.normpath(event.src_path))
        if texfile.endswith(".tex"):
            curr_hash = hash(texfile)
            if self.texfiles[texfile] != curr_hash:
                print("[ Recompiling {} ({}) ]".format(texfile, self.counts[texfile]))
                self.texfiles[texfile] = curr_hash
                subprocess.run("texify -b {}".format(texfile), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                subprocess.run("dvipdfm {}.dvi".format(texfile[:-4]), shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                self.counts[texfile] += 1
                self.error_check(texfile[:-4])
    def error_check(self, fname):
        with open("{}.log".format(fname)) as log:
            lines = []
            for line in log:
                if "I suspect" in line:
                    print(line.split(",")[0].strip())
                if "!" in line:
                    print(line.strip())
                    print("   ", "    ".join(lines))
                    break

                if len(lines) < 2:
                    lines.append(line)
                else:
                    lines.append(line)
                    lines.pop(0)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    event_handler = LatexHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print("[ TeXMex Debugging Mode ]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[ Cleaning Up ]")
        cleanup()
        print("[ Quitting ]")
        observer.stop()
    observer.join()
