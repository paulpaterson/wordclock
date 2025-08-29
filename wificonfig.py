"""Responsible for configuring the WIFI by the clock reading a QR code"""

from __future__ import annotations
import enum
import subprocess
import warnings
from typing import TYPE_CHECKING

try:
    import qrcode
except ImportError as e:
    warnings.warn(f'Could not load qrcode module - is camera loaded?: {e}')

if TYPE_CHECKING:
    from clock_updater import Updater

class WifiConfigStage(enum.Enum):
    IDLE = 'idle'
    READING_QR_CODE = 'trying to read qr code'
    WAITING_TO_JOIN_NETWORK = 'waiting to join network'
    NO_QR_READ = 'no QR could be read'
    NETWORK_NOT_JOINED = 'network could not be joined'
    NETWORK_JOINED = 'network joined'


class WifiConfigurator:
    """The class responsible for moving through the config stages"""

    def __init__(self, updater: Updater, qrcode_file: str="") -> None:
        """Initialise the configurator"""
        self.updater = updater
        self.wifi_stage = WifiConfigStage.IDLE
        self.max_retries = 4
        self.wifi_details: dict[str, str] = {}
        self.fixed_qrcode_filename = qrcode_file

    def start_reading(self) -> WifiConfigStage:
        """Start trying to read the QR code"""
        self.wifi_stage = WifiConfigStage.READING_QR_CODE
        self.updater.config_mode.top = True
        self.updater.config_mode.right = False
        self.updater.config_mode.left = False
        self.updater.config_mode.bottom = True
        #
        # Try to rad the QR code to get the network details
        self.read_qr_code()
        if self.wifi_stage == WifiConfigStage.WAITING_TO_JOIN_NETWORK:
            self.updater.config_mode.top = False
            self.updater.config_mode.bottom = False
            self.updater.config_mode.left = True
            self.updater.config_mode.right = True
            #
            # Set these as the network settings and try to connect to that
            # network
            self.make_network_change()
            #
            if self.wifi_stage == WifiConfigStage.NETWORK_JOINED:
                # Connected!
                self.updater.config_mode.color = (0, 255, 0)
            else:
                # Not connected!
                self.updater.config_mode.color = (255, 0, 0)
        else:
            #
            # Failed to get network details
            self.updater.config_mode.color = (255, 0, 0)
        #
        self.updater.config_mode.top = True
        self.updater.config_mode.right = True
        self.updater.config_mode.left = True
        self.updater.config_mode.bottom = True
        #
        self.update_board()
        return self.wifi_stage

    def update_board(self) -> None:
        """Update the display on the clock"""
        logs = self.updater.update_board()
        self.updater.board.show_board(logs)

    def go_idle(self) -> None:
        """Move back to idle"""
        self.wifi_stage = WifiConfigStage.IDLE

    def read_qr_code(self) -> None:
        """Read the QR code"""
        on = False
        for _ in range(self.max_retries):
            #
            # Flash the top bar
            self.updater.config_mode.color = (255, 255, 255) if on else (100, 100, 255)
            on = not on
            self.update_board()
            #
            # Try to get a QR code
            result = self.get_qr()
            if result:
                self.wifi_stage = WifiConfigStage.WAITING_TO_JOIN_NETWORK
                return
        else:
            self.wifi_stage = WifiConfigStage.NO_QR_READ

    def get_qr(self) -> bool:
        """Make one attempt to get the QR code and return the data or None if none found"""
        result = qrcode.detect_mode(4, self.fixed_qrcode_filename)
        if not result:
            return False
        else:
            details = qrcode.get_wifi_details_from_qr(result)
            if not details:
                return False
            else:
                self.wifi_details = details
                return True

    def make_network_change(self) -> None:
        """Set the network properties from the QR code"""
        try:
            result = subprocess.run(
                [
                    'sudo',
                    './scripts/configure_network.sh',
                    '--ssid', self.wifi_details['SSID'],
                    '--password', self.wifi_details['PASSWORD'],
                    '--security', self.wifi_details['SECURITY'],
                    '--wait', '20',
                ],
                capture_output=False, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f'Failed: {e}')
            self.wifi_stage = WifiConfigStage.NETWORK_NOT_JOINED
        else:
            self.wifi_stage = WifiConfigStage.NETWORK_JOINED


