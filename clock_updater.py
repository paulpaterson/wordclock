"""Class to handle updating the clock face and edges"""

from __future__ import annotations
import sys
import enum
import os
import datetime
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Callable, Any

import blessed

import modes
import setdate
import wificonfig

if TYPE_CHECKING:
    from run_clock import Board

class UpdateModes(enum.Enum):
    NORMAL = 'normal'               # Action button cycles modes
    CONFIG_HOURS = 'config hours'   # Action button advances hours
    CONFIG_MINS = 'config mins'     # Action button advances minutes
    CONFIG_WIFI = 'config WIFI'     # Action button triggers to start scanning for QR code


class Updater:
    """A class to manage updating the clock"""

    def __init__(self, board: Board, current_offset: timedelta, term: blessed.Terminal, interval: float,
                 simulation_offset: timedelta, lights: Callable[[int], Any]|None,
                 button_key: str, mode_button_key: str, set_system_time: bool, qrcode_file: str):
        self.mode = UpdateModes.NORMAL
        self.wifi_config = wificonfig.WifiConfigurator(self, qrcode_file)
        self.board = board
        self.current_offset = current_offset
        self.term = term
        self.interval = interval
        self.simulation_offset = simulation_offset
        self.lights = lights
        self.button_key = button_key
        self.mode_button_key = mode_button_key
        self.set_system_time = set_system_time
        self.old_modes = board.modes
        self.config_mode = modes.ConfigMode(None)
        self.config_modes = [self.config_mode, modes.Normal(None)]
        self.last_key_press = time.time()
        self.mode_cancel_timer: int = 0
        self.edge_modes = [mode(None) for mode in modes.modes.values() if mode.include_as_dynamic]

    def update_board(self) -> list[str]:
        """Update the display of the clock"""
        logs = self.board.update_board()
        self.board.show_board(logs)
        return logs

    def update(self) -> None:
        last_config_time = os.path.getmtime('config/config.sh')
        while True:
            try:
                t = datetime.datetime.now()
                self.board.time = (t + self.current_offset).time()
                #
                with self.term.cbreak():
                    if pressed := self.term.inkey(timeout=self.interval):
                        if pressed == self.button_key:
                            self.mode_button_press()
                        elif pressed == self.mode_button_key:
                            self.action_button_press()
                        else:
                            break
                if self.mode == UpdateModes.CONFIG_WIFI:
                    result = self.wifi_config.start_reading()
                    self.mode = UpdateModes.NORMAL
                    if result == wificonfig.WifiConfigStage.NETWORK_JOINED:
                        self.board.modes = [modes.ShowIPAddress(None)]
                    else:
                        self.last_key_press = time.time()
                #
                # Set the lights to show we are now in active config
                if self.mode != UpdateModes.NORMAL:
                    self.config_mode.set_edges_from_int(self.mode_cancel_timer)
                    self.mode_cancel_timer -= 1
                    if self.mode_cancel_timer < 0:
                        self.reset_config()
                #
                logs = self.update_board()
                self.update_board()
                #
                self.current_offset += self.simulation_offset
            except KeyboardInterrupt:
                print('CTRL-C detected')
                break
            if os.path.getmtime('config/config.sh') != last_config_time:
                sys.exit(2)

        if self.lights and self.board.lights:
            self.board.lights.clear_strip()
            self.board.lights.update_strip()

    def action_button_press(self) -> None:
        """Move to the next edge mode"""
        if self.mode == UpdateModes.NORMAL:
            new_mode: list[modes.Mode] = []
            new_edge_mode = self.edge_modes.pop(0)
            if new_edge_mode.type == modes.FaceModeType.EDGE:
                new_mode.append(modes.Normal(None))
            new_mode.append(new_edge_mode)
            self.edge_modes.append(new_edge_mode)
            self.board.modes = new_mode
        if self.mode == UpdateModes.CONFIG_HOURS:
            self.current_offset += datetime.timedelta(hours=1)
        elif self.mode == UpdateModes.CONFIG_MINS:
            self.current_offset += datetime.timedelta(minutes=5)
        #
        self.mode_cancel_timer = 4

    def reset_config(self) -> None:
        """Reset back to normal mode"""
        #
        # Reset the modes
        self.mode = UpdateModes.NORMAL
        self.wifi_config.go_idle()
        self.board.modes = self.old_modes
        if self.config_mode.on:
            # If it was on then turn it off to clear the config display
            self.config_mode.color = (0, 0, 0)
            self.config_mode.update(self.board)
            self.config_mode.color = (255, 0, 0)
        #
        # Change the system date if needed
        if self.set_system_time:
            now = datetime.datetime.now()
            new_time = now + self.current_offset
            setdate.set_system_date(new_time)
            self.current_offset = datetime.timedelta()


    def mode_button_press(self) -> None:
        """The button was released"""
        if self.mode == UpdateModes.NORMAL:
            self.mode = UpdateModes.CONFIG_HOURS
            self.board.modes = self.config_modes
            self.config_mode.color = (255, 0, 255)
        elif self.mode == UpdateModes.CONFIG_HOURS:
            self.mode = UpdateModes.CONFIG_MINS
            self.config_mode.color = (255, 255, 0)
        elif self.mode == UpdateModes.CONFIG_MINS:
            self.mode = UpdateModes.CONFIG_WIFI
            self.config_mode.color = (100, 100, 255)
        else:
            self.reset_config()

        self.mode_cancel_timer = 4

