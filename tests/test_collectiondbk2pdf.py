import unittest

import time
import subprocess

try:
    import cv2
except ImportError:
    raise RuntimeError("Module cv2 not found. Try running"
                       "'apt-get install libopencv-dev python-opencv'")

from os import listdir
from os.path import isfile, join, exists

import collectiondbk2pdf

from wand.image import Image
from util import mean_squared_error

OUTPUT_DIR = "./tests/test_output"
INPUT_DIR = "./tests/test_data"
COLLECTION = "col11287_1.1_complete"
PRINCE_PATH = "/usr/bin/prince"
STYLE = "ccap-physics"


class Test_collectiondbk2pdf(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not exists(join(INPUT_DIR, COLLECTION)):
            if exists(join(INPUT_DIR, COLLECTION + ".zip")):
                command = ["unzip", join(
                    INPUT_DIR, COLLECTION + ".zip"), "-d", INPUT_DIR]
                sproc = subprocess.Popen(command)
                sproc.wait()
        command = ["mkdir", OUTPUT_DIR]
        sproc = subprocess.Popen(command)
        sproc.wait()
        cls.setup_command = ["collectiondbk2pdf",
                             "-p", PRINCE_PATH,
                             "-d", join(INPUT_DIR, COLLECTION),
                             "-s", STYLE,
                             join(OUTPUT_DIR, "test_results.pdf")]
        start_time = time.time()
        collectiondbk2pdf.main(cls.setup_command[1:])
        cls.setup_runtime = time.time() - start_time
        print("---setUpClass: script=collectiondbk2pdf input={1} runtime={0} seconds ---".format(
            cls.setup_runtime, COLLECTION))

    @classmethod
    def tearDownClass(cls):
        command = ["rm", "-rf", OUTPUT_DIR]
        sp = subprocess.Popen(command)
        sp.wait()

    def test_class_setup(self):
        pass

    def test_pdf_gen_accuracy(self):
        with Image(filename=join(INPUT_DIR, 'expected.pdf')) as img:
            img.format = 'png'
            img.save(filename=join(OUTPUT_DIR, 'expected.png'))

        with Image(filename=join(OUTPUT_DIR, "test_results.pdf")) as img:
            img.format = 'png'
            img.save(filename=join(OUTPUT_DIR, "test_results.png"))

        expected_files_list = [join(OUTPUT_DIR, f) for f in listdir(
            OUTPUT_DIR) if isfile(join(OUTPUT_DIR, f)) and "png" in f and "expected" in f]
        actual_files_list = [join(OUTPUT_DIR, f) for f in listdir(
            OUTPUT_DIR) if isfile(join(OUTPUT_DIR, f)) and "png" in f and "test" in f]

        self.assertEqual(len(expected_files_list), len(actual_files_list))

        expected_files_list.sort()
        actual_files_list.sort()

        for i in range(0, len(expected_files_list)):
            expected_image = cv2.imread(expected_files_list[i])
            actual_image = cv2.imread(actual_files_list[i])
            img_cmp_messure = mean_squared_error(expected_image, actual_image)
            self.assertEqual(img_cmp_messure, 0.0)

if __name__ == '__main__':
    unittest.main()
