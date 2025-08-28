"""Read config by using the camera to look at text"""

import easyocr  # type: ignore
import pathlib
import pprint
import cv2
import numpy as np


def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)

    return sharpened

def ocr_text(name, sharpen, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    test_file = pathlib.Path('images', name)
    img = cv2.imread(str(test_file))
    if sharpen:
        img = unsharp_mask(img, kernel_size, sigma, amount, threshold)
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)

    items = [text for  _, text, _ in result]
    return items

for name in (
#        'simple_test_1.jpg',
#        'simple_test_2.jpg',
        'simple_test_3.jpg',
        'simple_test_4.jpg',
#        'simple_test_3_sharp.jpg'
):
    for kernel in (3, 5, 7):
        for amount in (0.7, 0.8, 0.9):
            items = ocr_text(name, True, amount=amount, kernel_size=[kernel, kernel])
            print(f'Processing {name} with {name=}, {amount=}, {kernel=}...')
            items.append('')
            print('. '.join(items))

            print('Done!\n')

    print()

