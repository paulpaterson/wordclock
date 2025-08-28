import pytest
import subprocess
import re

def test_get_ip_address():
    """Check we can get an IP address from the script"""
    result = subprocess.run(['../scripts/getip.sh'], capture_output=True)
    ip = result.stdout.decode('utf-8').strip()
    assert re.match('\d+\.\d+\.\d+\.\d+', ip)
    assert result.returncode == 0