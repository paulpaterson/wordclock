"""Reading data from a QR code"""
import io
import subprocess
import pathlib
from PIL import Image
from resizeimage import resizeimage
import tempfile
import os
import sys
import re


def raw_get_qr_code(filename: pathlib.Path, resize: str="resize", width: int=400) -> str:
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
                    the_file_name = pathlib.Path(fp.name)
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

    return result

def get_qr_code(filename: pathlib.Path) -> str|None:
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


def capture_frame(filename: pathlib.Path, timeout: float=1) -> None:
    """Capture a frame from the camera"""
    print("Capturing ...", end="")
    result = subprocess.run([
            "rpicam-still", "-t",  f"{timeout}s",  
            "--autofocus-mode", "continuous",
            "--nopreview",
            "-o",  filename
    ], capture_output=True)
    print("Done!")
    return None


def detect_mode(max_iterations: int, fixed_filename: str="") -> str | None:
    """Continuously try to detect a QR code"""
    filename = fixed_filename if fixed_filename else pathlib.Path(__file__).parent / "images" / "detect.jpg"
    iteration = max_iterations
    while iteration:
        if not fixed_filename:
            capture_frame(pathlib.Path(filename), 0.01)
        result = get_qr_code(pathlib.Path(filename))
        if result:
            print(f"We got a QR code for: {result}")
            return result
        else:
            print("Nothing detected")
            iteration -= 1
    return None

def get_wifi_details_from_qr(qr_string: str) -> dict[str, str]:
    """Return the WIFI details from a code read form the camera"""
    if not qr_string.startswith('WIFI:'):
        return {}
    parts = {}
    for part_type, part_value in re.findall('(\w):([^;]*);', qr_string[5:]):
        parts[part_type] = part_value
    print(parts)
    return {
        'SECURITY': parts.get('T', 'unknown'),
        'SSID': parts.get('S', 'unknown'),
        'PASSWORD': parts.get('P', 'unknown'),
    }


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'detect':
            while True:
                result = detect_mode(10)
                if result:
                    print(get_wifi_details_from_qr(result))
                else:
                    print('No result!')
        else:
            print(get_qr_code(pathlib.Path(__file__).parent / sys.argv[1]))
    else:
        print('Usage: python qrcode.py <filename>, <optionally: resize>')
