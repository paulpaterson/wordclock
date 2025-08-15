from ipaddress import ip_address

from flask import Flask, request, jsonify, render_template
import os
import re
import socket
import sys
import faces
import modes
import subprocess

app = Flask(__name__)

# Configuration file path
CONFIG_FILE = "config/config.sh"

def load_config():
    """
    Loads the configuration from the config.sh file.
    Returns a dictionary with the configuration parameters.
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                for line in f:
                    # Use regex to find lines that start with CLOCK_ and have an assignment
                    match = re.match(r"^export\s(CLOCK_[\w_]+)=(.*)$", line)
                    if match:
                        key, value = match.groups()
                        config[key] = value.strip().strip('"')  # Remove extra quotes
        except Exception as e:
            print(f"Error reading config file: {e}")
            # Consider logging the error or raising an exception
    return config


def save_config(data):
    """
    Saves the configuration to the config.sh file.
    Args:
        data (dict): A dictionary with the configuration parameters.
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            for key, value in data.items():
                # Quote the values to handle spaces and special characters
                f.write(f"export {key}=\"{value}\"\n")
            f.write('export CLOCK_LIGHT_MODE="detect"\n')
    except Exception as e:
        print(f"Error writing config file: {e}")
        return False  # Indicate failure
    return True


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """
    Handles GET requests to retrieve the current configuration and
    POST requests to update the configuration.
    """
    if request.method == 'GET':
        global CLOCK_IP
        config = load_config()
        config['VALID_MODES'] = modes.get_valid_modes()
        config['VALID_FACES'] = faces.get_valid_faces()
        config['CLOCK_IP_ADDRESS'] = CLOCK_IP
        return jsonify(config)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            # Basic validation of input data
            required_keys = [
                "CLOCK_SHOW_IT_IS",
                "CLOCK_SHOW_A",
                "CLOCK_INTERVAL",
                "CLOCK_LIGHT_COLOR",
                "CLOCK_FACE_MODE",
                "CLOCK_MODE",
                "CLOCK_BAUD_RATE",
                "CLOCK_IP_ADDRESS",
            ]
            if not all(key in data for key in required_keys):
                return jsonify({"error": "Missing parameters in request"}), 400

            # Convert interval to float
            try:
                interval = float(data["CLOCK_INTERVAL"])
                if interval < 0:
                    raise ValueError("Interval must be a positive number")
            except ValueError as e:
                return jsonify({"error": f"Invalid value for CLOCK_INTERVAL: {e}"}), 400

            # Color validation (basic check for '#' and 6 hex characters)
            if not re.match(r"^#[0-9a-fA-F]{6}$", data["CLOCK_LIGHT_COLOR"]):
                return jsonify(
                    {"error": "Invalid value for CLOCK_LIGHT_COLOR.  Must be in #RRGGBB format"}
                ), 400

            if not isinstance(data["CLOCK_SHOW_A"], str) or data["CLOCK_SHOW_A"].lower() not in ["true", "false"]:
                return jsonify({"error": "Invalid value for CLOCK_SHOW_A.  Must be 'True' or 'False'"}), 400

            if not isinstance(data["CLOCK_SHOW_IT_IS"], str) or data["CLOCK_SHOW_IT_IS"].lower() not in ["true", "false"]:
                return jsonify({"error": "Invalid value for CLOCK_SHOW_IT_IS.  Must be 'True' or 'False'"}), 400

            # Face mode validation
            valid_face_modes = faces.get_valid_faces()
            if data["CLOCK_FACE_MODE"] not in valid_face_modes:
                return jsonify({"error": f"Invalid value for CLOCK_FACE_MODE. Must be one of {valid_face_modes}"}), 400

            # Mode validation (check if it's a list and all values are valid)
            if not isinstance(data["CLOCK_MODE"], list):
                return jsonify({"error": "Invalid value for CLOCK_MODE.  Must be a list."}), 400
            valid_modes = modes.get_valid_modes()
            for mode in data["CLOCK_MODE"]:
                if mode not in valid_modes:
                    return jsonify(
                        {"error": f"Invalid value in CLOCK_MODE: {mode}.  Must be one of {valid_modes}"}
                    ), 400
            #join the modes to be saved as a space separated string
            data["CLOCK_MODE"] = " ".join(data["CLOCK_MODE"])

            # Baud rate validation
            try:
                baud_rate = int(data["CLOCK_BAUD_RATE"])
                if baud_rate <= 0:
                    raise ValueError("Baud rate must be a positive integer")
            except ValueError as e:
                return jsonify({"error": f"Invalid value for CLOCK_BAUD_RATE: {e}"}), 400

            # IP address validation
            try:
                ip_address = data["CLOCK_IP_ADDRESS"]
            except KeyError as e:
                return jsonify({"error": f"No value found for IP ADDRESS {e}"}), 400

            success = save_config(data)
            if success:
                return jsonify({"message": "Configuration saved successfully"})
            else:
                return jsonify({"error": "Failed to save configuration"}), 500  # Internal Server Error
        except Exception as e:
            return jsonify({"error": f"Error processing request: {e}"}), 400  # Bad Request


@app.route('/getmodes', methods=['GET'])
def get_modes():
    """
    Return any valid modes for the clock face
    """
    return jsonify(modes.get_valid_modes())

@app.route('/', methods=['GET'])
def show_config_page():
    """
    Handles GET requests to the /config route by rendering the config.html template.
    """
    return render_template('config.html')

@app.route('/config', methods=['GET'])
def legacy_config():
    return show_config_page()

@app.route('/api/software_update', methods=['GET'])
def do_software_update():
    try:
        result = subprocess.run(["./scripts/update_system.sh"], capture_output=True, text=True, check=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e.stderr}")
        raise
    return 'OK'

def get_my_ip():
    """
    Gets the current machine's IP address.  This method is more robust
    than methods that rely on external internet connections, as it works
    even when the machine is not connected to the internet.

    It creates a UDP socket and connects to a known external IP (Google's
    public DNS) on an arbitrary port.  The socket doesn't actually send
    any data, but the operating system automatically assigns the socket
    an IP address.  This IP address can then be retrieved using
    getsockname().  The socket is then closed.

    Returns:
        str: The machine's IP address as a string (e.g., "192.168.1.10"),
             or None if an error occurs.
    """
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a known external IP address and port.
        # Google's public DNS is used here, but any reliable external server
        # can be used.  The port number (8.8.8.8) is arbitrary.
        s.connect(("8.8.8.8", 80))
        # Get the IP address assigned to the socket by the OS.
        # This is the machine's local IP address on the network.
        ip_address = s.getsockname()[0]
        s.close()  # Close the socket to free up resources
        return ip_address
    except socket.error as e:
        print(f"Error getting IP address: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ui_backend.py <IPADDRESS>')
        sys.exit(2)
    CLOCK_IP = ip_address = sys.argv[1]
    print(f'Starting - binding to IP {ip_address}')
    app.run(host=ip_address, debug=True, port=8000)

