import pytest
import subprocess
import re
import pathlib

def test_get_ip_address():
    """Check we can get an IP address from the script"""
    path = pathlib.Path(__file__).parent.parent / 'scripts' / 'getip.sh'
    result = subprocess.run([path], capture_output=True)
    ip = result.stdout.decode('utf-8').strip()
    assert re.match('\d+\.\d+\.\d+\.\d+', ip)
    assert result.returncode == 0