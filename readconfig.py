"""Read config by using the camera to look at text"""

import easyocr
import pathlib
import pprint

for name in ('simple_test_1.jpg', 'simple_test_2.jpg', 'simple_test_3.jpg', 'simple_test_3_sharp.jpg'):
    print(f'Processing {name} ...', end=' ')
    test_file = pathlib.Path('images', name)
    reader = easyocr.Reader(['en'])
    result = reader.readtext(str(test_file))
    print('Done!\n')
    pprint.pprint(result)

