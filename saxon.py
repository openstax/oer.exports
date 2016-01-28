import subprocess
import os
from signal import SIGTERM

SAXON_PATH = "./lib/saxon9he.jar"
DELIMINATOR = "END_OF_XML_BLOCK"
MATH2SVG_PATH = "./xslt2/math2svg-in-docbook.xsl"

import threading
import thread

always_error = False

def error():
    thread.interrupt_main()

class Saxon:

    def __init__(self, saxon_path=SAXON_PATH, math2svg_path=MATH2SVG_PATH):
        math2svg_path = os.path.abspath(math2svg_path)
        saxon_path = os.path.abspath(saxon_path)

        if not os.path.exists(saxon_path):
             raise IOError("File: %s not found" % (saxon_path,))
        if not os.path.isfile(math2svg_path):
             raise IOError("File: %s not found" % (math2svg_path,))

        self.compile_cmd = "javac -cp %s SaxonTransformWrapper.java" % (
            os.path.basename(saxon_path),)
        self.process = subprocess.Popen(self.compile_cmd.split(),
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        close_fds=True,
                                        cwd=os.path.dirname(saxon_path))
        self.process.wait()

        saxon_class_path = os.path.join(os.path.dirname(
            saxon_path), "SaxonTransformWrapper.class")
        if not os.path.isfile(saxon_class_path):
             raise IOError("File: %s not found" % (saxon_class_path,))

        self.start_cmd = "java "\
                         "-cp saxon9he.jar:.:%s SaxonTransformWrapper "\
                         "-s:- -xsl:%s "\
                         "-deliminator:%s " % (saxon_path,
                                                   math2svg_path,
                                                   DELIMINATOR)

        self.process = subprocess.Popen(self.start_cmd.split(),
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        close_fds=True,
                                        cwd=os.path.dirname(saxon_path))
    def convert(self, xml):
        global always_error
        if always_error:
            raise RuntimeError
        error_countdown = threading.Timer(60.0,error)
        try:
            error_countdown.start()

            self.process.stdin.write(xml)
            self.process.stdin.write("\n" + DELIMINATOR + "\n")
            self.process.stdin.flush()
            process_info = ''
            process_info_line = ''

            while DELIMINATOR not in process_info_line:
                process_info = process_info + process_info_line
                process_info_line = self.process.stderr.readline()

    
            svg = ''
            svg_line = ''
            while DELIMINATOR not in svg_line:
                svg = svg + svg_line
                svg_line = self.process.stdout.readline()
    
            svg = svg.strip()
    
            error_countdown.cancel()
        except KeyboardInterrupt:
            always_error = True
            raise RuntimeError
        return svg

    def _flush(self):
        self.process.stdin.flush()
        self.process.stdout.flush()
        self.process.stderr.flush()

    def _close(self):
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()

    def stop(self):
        self._close()
        try:
            os.kill(self.process.pid,SIGTERM)
        except OSError:
            pass

