from PIL import Image
import numpy as np
import cv2

class ImageProcessor:

    def __greyScale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def __noiseremoval(self, image):
        kernal = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernal, iterations = 1)
        kernel = np.ones((1,1), np.uint8)
        image = cv2.erode(image, kernel, iterations = 1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        return image

    def __resize(self, image):
        desired_width = 900
        desired_height = 600

        # Resize the image
        resized_image = cv2.resize(image, (desired_width, desired_height))

        return resized_image


    def __thin_font(self, image):
        image = cv2.bitwise_not(image)
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.erode(image, kernel, iterations=2)
        image = cv2.bitwise_not(image)
        return image


    def sanitize(self, image_path):
        grey = self.__greyScale(cv2.imread(image_path))
        threshold, image_bw = cv2.threshold(grey, 150, 255, cv2.THRESH_BINARY)
        noNoiseImage = self.__noiseremoval(image_bw)
        noNoiseImage = self.__noiseremoval(noNoiseImage)
        # noNoiseImage = thin_font(noNoiseImage)
        # noNoiseImage = self.__resize(noNoiseImage)

        processed_image_rgb = cv2.cvtColor(noNoiseImage, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(processed_image_rgb)
        pil_image.save(image_path)


        return image_path
