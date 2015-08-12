import unittest

import subprocess
import resource

#from skimage.measure import structural_similarity as ssim
import numpy as np
import cv2

from os import listdir
from os.path import isfile, join

REPO_DIR="/opt/production/oer.exports"
COLLECTION_DIR="/opt/production/oer.exports/tests/test_data/test-ccap"
#COLLECTION_DIR=REPO_DIR+"/test-ccap"
PRINT_STYLE="ccap-physics"
TEST_DATA_DIR="/opt/production/oer.exports/tests/test_data"
OUTPUT_DIR="/opt/production/oer.exports/tests/test_output"
OUTPUT_PDF=REPO_DIR+"/tests/test_output/test_results.pdf"
OUTPUT_IMAGE_DIR=REPO_DIR+"/tests/test_output"
OUTPUT_IMAGE=OUTPUT_IMAGE_DIR+"/output.png"

# FIXME: move to utils
def mean_squared_error(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

class Test_opencv_functions(unittest.TestCase):
      def test_mean_squared_error(self):
          img1=cv2.imread(join(TEST_DATA_DIR,"test_image-1.png"))
          img2=cv2.imread(join(TEST_DATA_DIR,"test_image-2.png"))
          img_cmp_messure=mean_squared_error(img1,img1)
          self.assertEqual(img_cmp_messure,0.0)
          img_cmp_messure=mean_squared_error(img1,img2)
          self.assertNotEqual(img_cmp_messure,0.0)

class Test_collectiondbk2pdf(unittest.TestCase):

    # FIXME: think about how pdf can be save for git commit version

    @classmethod
    def setUpClass(cls): 
        command=["collectiondbk2pdf",
                 "-p", "/usr/bin/prince",
                 "-d", COLLECTION_DIR,
                 "-s", PRINT_STYLE,
                 OUTPUT_PDF]
        subprocess.call(command)
        info = resource.getrusage(resource.RUSAGE_CHILDREN)
        print("\n\n")
        print(info)

        command= ["convert",
                  "-density", "150",
                  OUTPUT_PDF, 
                  "-quality", "100", 
                  OUTPUT_IMAGE]
        subprocess.call(command)

    @classmethod
    def tearDownClass(cls):
        command=["rm", "-rf" , OUTPUT_DIR]
        subprocess.call(command)
        command=["mkdir", OUTPUT_DIR]
        subprocess.call(command)

    def test_class_setup(self):
        pass

    def test_pdf_gen_accuracy(self):
       test_files_list = [ f for f in listdir(TEST_DATA_DIR) if isfile(join(TEST_DATA_DIR,f)) and "png" in f]
       output_files_list = [ f for f in listdir(OUTPUT_DIR) if isfile(join(OUTPUT_DIR,f)) and "png" in f]
       self.assertEqual(len(test_files_list),len(output_files_list))
       test_files_list.sort()
       output_files_list.sort()
       for i in range(0,len(test_files_list)):
           test_image_path = join(TEST_DATA_DIR,test_files_list[i])
           output_image_path = join(OUTPUT_DIR,output_files_list[i])
           original_img = cv2.imread(test_image_path)
           new_img = cv2.imread(output_image_path)
           img_cmp_messure=mean_squared_error(original_img,new_img)
           self.assertEqual(img_cmp_messure,0.0)          


if __name__ == '__main__':
    unittest.main()

