"""Reading data from a QR code"""
import io
import subprocess
import pathlib
from PIL import Image
from resizeimage import resizeimage
import tempfile
import os
import sys


def raw_get_qr_code(filename, resize="resize", width=400):
    if sys.platform == 'linux':
        zbar_app = 'zbarimg'
    else:
        zbar_root = pathlib.Path("/opt/homebrew/Cellar/zbar/0.23.93_2/bin")
        zbar_app = (zbar_root / "zbarimg").as_posix()

    root = pathlib.Path(__file__).parent.parent
    image_file = root / filename

    #
    # Get file and resize
    with tempfile.NamedTemporaryFile('wb', suffix='.jpg', delete=False) as fp:
        with open(image_file, 'r+b') as f:
            if resize == 'resize':
                with Image.open(f) as image:
                    resized = resizeimage.resize_width(image, width)
                    byte_stream = io.BytesIO()
                    resized.save(byte_stream, format="JPEG")
                    fp.write(byte_stream.getvalue())
                    fp.close()
                    the_file_name = fp.name
            else:
                the_file_name = image_file

        output = subprocess.run(
            [zbar_app, the_file_name],
            capture_output=True
        )
        fp.delete = True
        #print('Temp file: ', fp.name)

    os.remove(fp.name)

    #print(output)

    code = output.stdout.split(b":", maxsplit=1)
    result = code[1].decode('utf-8').strip()
    #print(f'Code is "{result}"')
    return result

def get_qr_code(filename):
    """Try to get the QR code from an image file"""
    try:
        result = raw_get_qr_code(filename, 'resize')
    except Exception as e1:
        try:
            result = raw_get_qr_code(filename, 'noresize')
        except Exception as e2:
            print('Error - no conversion worked:', e1, e2)
            return None
    return result



if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(get_qr_code(sys.argv[1]))
    else:
        print('Usage: python qrcode.py <filename>, <optionally: resize>')
