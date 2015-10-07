import subprocess
import os

SAXON_PATH = "./lib/saxon9he.jar"
DELIMINATOR = "END_OF_XML_BLOCK"
MATH2SVG_PATH = "./xslt2/math2svg-in-docbook.xsl"


class Saxon:

    def __init__(self, saxon_path=SAXON_PATH, math2svg_path=MATH2SVG_PATH):
        math2svg_path = os.path.abspath(math2svg_path)
        saxon_path = os.path.abspath(saxon_path)

        if not os.path.exists(saxon_path):
             raise IOError("File: {} not found".format(saxon_path))
        if not os.path.isfile(math2svg_path):
             raise IOError("File: {} not found".format(math2svg_path))

        self.compile_cmd = "javac -cp {} SaxonTransformWrapper.java".format(
            os.path.basename(saxon_path))
        self.process = subprocess.Popen(self.compile_cmd.split(),
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        close_fds=True,
                                        cwd=os.path.dirname(saxon_path))
        self.process.wait()

        saxon_class_path = os.path.join(os.path.dirname(saxon_path),"SaxonTransformWrapper.class")
        if not os.path.isfile(saxon_class_path):
             raise IOError("File: {} not found".format(saxon_class_path))
       

        self.start_cmd = "java "\
                         "-cp saxon9he.jar:.:{0} SaxonTransformWrapper "\
                         "-s:- -xsl:{1} "\
                         "-deliminator:{2}".format(saxon_path, 
                                                   math2svg_path, 
                                                   DELIMINATOR)

        self.process = subprocess.Popen(self.start_cmd.split(),
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        close_fds=True,
                                        cwd=os.path.dirname(saxon_path))


    def convert(self, xml):
        self.process.stdin.write(xml)
        self.process.stdin.write("\n" + DELIMINATOR + "\n")
        process_info = self.process.stderr.readline()
        while "LOG: INFO: MathML2SVG" not in process_info:
            process_info = self.process.stderr.readline()
            if "Error" in process_info:
                break;
        if "LOG: INFO: MathML2SVG" in process_info:
            pass
        elif "Error" in process_info:
            self.process.terminate()
            returncode = self.process.wait()
            process_info = "Error reported by XML parser: " + process_info
            raise subprocess.CalledProcessError(
                returncode, self.start_cmd, process_info)
        svg_line = ''
        svg_list = []
        while DELIMINATOR not in svg_line:
            svg_list.append(svg_line)
            svg_line = self.process.stdout.readline()
        self._flush()
        svg = '\n'.join(svg_list).strip()
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
        self.process.terminate()
        self.process.wait()

