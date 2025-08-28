"""Class to handle updating the clock face and edges"""

import sys
import enum
import os
import datetime
import time

import modes
import setdate
import wificonfig


class UpdateModes(enum.Enum):
    NORMAL = 'normal'
    CONFIG_HOURS = 'config hours'
    CONFIG_MINS = 'config mins'
    CONFIG_WIFI = 'config WIFI'



class Updater:
    """A class to manage updating the clcck"""

    def __init__(self, board, current_offset, term, interval,
                 simulation_offset, lights, button_key, mode_button_key, set_system_time, qrcode_file):
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
        self.button_reset_interval = 5
        self.button_mins_interval = 0.5
        self.button_click = 0
        self.edge_modes = [mode(None) for mode in modes.modes.values() if mode.type == modes.FaceModeType.EDGE]

    def update_board(self):
        """Update the display of the clock"""
        return self.board.update_board()

    def update(self):
        last_config_time = os.path.getmtime('config/config.sh')
        while True:
            try:
                t = datetime.datetime.now()
                self.board.time = t + self.current_offset
                #
                logs = self.update_board()
                if self.mode != UpdateModes.NORMAL and time.time() - self.last_key_press > self.button_reset_interval:
                    self.reset_config()
                else:
                    self.board.show_board(logs)
                #
                with self.term.cbreak():
                    if pressed := self.term.inkey(timeout=self.interval):
                        if pressed == self.button_key:
                            self.button_up()
                        elif pressed == self.mode_button_key:
                            self.next_edge_mode()
                        else:
                            break
                    #
                    # Set the lights to show we are now in active config
                    if self.mode != UpdateModes.NORMAL and time.time() - self.last_key_press > self.button_mins_interval:
                        self.config_mode.right = True
                        self.config_mode.left = True

                self.current_offset += self.simulation_offset
            except KeyboardInterrupt:
                print('CTRL-C detected')
                break
            if os.path.getmtime('config/config.sh') != last_config_time:
                sys.exit(2)

        if self.lights:
            self.board.lights.clear_strip()
            self.board.lights.update_strip()

    def next_edge_mode(self):
        """Move to the next edge mode"""
        if self.mode == UpdateModes.NORMAL:
            new_mode = [modes.Normal(None)]
            new_edge_mode = self.edge_modes.pop(0)
            new_mode.append(new_edge_mode)
            self.edge_modes.append(new_edge_mode)
            self.board.modes = new_mode

    def reset_config(self):
        """Reset back to normal mode"""
        #
        # Reset the modes
        self.mode = UpdateModes.NORMAL
        self.wifi_config.go_idle()
        self.board.modes = self.old_modes
        self.button_click = 0
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


    def button_up(self):
        """The button was released"""
        if self.mode == UpdateModes.NORMAL:
            self.mode = UpdateModes.CONFIG_HOURS
            self.board.modes = self.config_modes
            self.config_mode.right = False
            self.config_mode.left = False
            self.button_click = 0
        elif self.mode == UpdateModes.CONFIG_HOURS and time.time() - self.last_key_press < self.button_mins_interval and self.button_click == 0:
            self.mode = UpdateModes.CONFIG_MINS
            self.config_mode.color = (255, 255, 0)
            self.config_mode.right = False
            self.config_mode.left = False
        elif self.mode == UpdateModes.CONFIG_MINS and time.time() - self.last_key_press < self.button_mins_interval and self.button_click == 0:
            self.mode = UpdateModes.CONFIG_WIFI
            self.wifi_config.start_reading()
        else:
            if self.mode == UpdateModes.CONFIG_HOURS:
                self.current_offset += datetime.timedelta(hours=1)
            elif self.mode == UpdateModes.CONFIG_MINS:
                self.current_offset += datetime.timedelta(minutes=5)
            self.button_click += 1
        self.last_key_press = time.time()
