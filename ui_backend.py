from flask import Flask, request, jsonify, render_template
import os
import re

app = Flask(__name__)

# Configuration file path
CONFIG_FILE = "config.sh"

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
                    match = re.match(r"^(CLOCK_[\w_]+)=(.*)$", line)
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
                f.write(f"{key}=\"{value}\"\n")
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
        config = load_config()
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
            valid_face_modes = ["10x11", "14x5", "16x16"]
            if data["CLOCK_FACE_MODE"] not in valid_face_modes:
                return jsonify({"error": f"Invalid value for CLOCK_FACE_MODE. Must be one of {valid_face_modes}"}), 400

            # Mode validation (check if it's a list and all values are valid)
            if not isinstance(data["CLOCK_MODE"], list):
                return jsonify({"error": "Invalid value for CLOCK_MODE.  Must be a list."}), 400
            valid_modes = ["Normal", "EdgeLightSeconds", "TestEdge", "TestWords", "FlashWords"]
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

            success = save_config(data)
            if success:
                return jsonify({"message": "Configuration saved successfully"})
            else:
                return jsonify({"error": "Failed to save configuration"}), 500  # Internal Server Error
        except Exception as e:
            return jsonify({"error": f"Error processing request: {e}"}), 400  # Bad Request


@app.route('/config', methods=['GET'])
def show_config_page():
    """
    Handles GET requests to the /config route by rendering the config.html template.
    """
    return render_template('config.html')


if __name__ == '__main__':
    app.run(debug=True)

