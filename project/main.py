import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets import WIFI_SSID, WIFI_PASSWORD

demo_line = "1"

demo_departures = [
    ("08:00", "Karlskrona Centralstation", "On time"),
    ("08:01", "Karlskrona Lokstallarna", "On time"),
    ("08:02", "Tullskolan Karlskrona", "On time"),
    ("08:03", "Polhemsgatan Karlskrona", "On time"),
    ("08:05", "Campus Gräsvik", "On time"),
]


class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        self.tile1_dark = False
        self.tile2_dark = False
        self.tile3_dark = False
        self.create_ui()
        self.connect_wifi()
        log("student application ready")

    @staticmethod
    def apply_tile_colors(tile, label, dark):
        tile.set_style_bg_opa(lv.OPA.COVER, 0)
        tile.set_style_bg_color(
            lv.color_hex(0x000000 if dark else 0xFFFFFF), 0
        )
        label.set_style_text_color(
            lv.color_hex(0xFFFFFF if dark else 0x000000), 0
        )

    def on_tile_clicked(self, _event):
        self.tile1_dark = not self.tile1_dark
        self.tile2_dark = not self.tile2_dark
        self.tile3_dark = not self.tile3_dark
        self.apply_tile_colors(self.tile1, self.tile1_label, self.tile1_dark)
        self.apply_tile_colors(self.tile2, self.tile2_label, self.tile2_dark)
        self.apply_tile_colors(self.tile3, self.tile3_label, self.tile3_dark)

        if self.tile1_dark:
            self.theme_dropdown.set_selected(1)
        else:
            self.theme_dropdown.set_selected(0)

    def theme_changed(self, _event):
        selected_index = self.theme_dropdown.get_selected()

        if selected_index == 0:
            self.tile1_dark = False
            self.tile2_dark = False
            self.tile3_dark = False
        else:
            self.tile1_dark = True
            self.tile2_dark = True
            self.tile3_dark = True

        self.apply_tile_colors(self.tile1, self.tile1_label, self.tile1_dark)
        self.apply_tile_colors(self.tile2, self.tile2_label, self.tile2_dark)
        self.apply_tile_colors(self.tile3, self.tile3_label, self.tile3_dark)

    def stop_changed(self, _event):
        selected_index = self.stop_dropdown.get_selected()
        selected_departure = demo_departures[selected_index]
        self.selected_stop = selected_departure[1]

        departure_text = (

            "Departures - Line " + demo_line + "\n\n"
            + selected_departure[0] + " "
            + selected_departure[1] + " "
            + selected_departure[2] + "\n"
            + "\n\n\n\n<< Swipe>>"
        )

        self.tile2_label.set_text(departure_text)

    def transport_changed(self, _event):
        selected_index = self.transport_dropdown.get_selected()

        transport_types = [
            "Bus",
            "Train",
            "Ferry",
            "All"
        ]

        self.selected_transport = transport_types[selected_index]

    def create_ui(self):
        'Function: Creates UI'
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.tile1 = self.tileview.add_tile(0, 0, lv.DIR.RIGHT)
        self.tile2 = self.tileview.add_tile(1, 0, lv.DIR.LEFT | lv.DIR.RIGHT)
        self.tile3 = self.tileview.add_tile(2, 0, lv.DIR.LEFT)

        self.tile1_label = lv.label(self.tile1)
        self.tile1_label.set_text(
            "Public Transport Information\n\n"
            "Version 1.0\n\n"
            "(Group 14)\n"
            "Fadi Jabali\n"
            "Shahd Albader\n"
            "Molham Saffour\n"
            "Harout Kansabedien\n"
            "Emil Gazal\n\n\n"
            "Swipe >>"
        )
        self.tile1_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile1_label.center()
        self.apply_tile_colors(self.tile1, self.tile1_label, False)
        self.tile1.add_event_cb(
            self.on_tile_clicked, lv.EVENT.CLICKED, None
        )

        departure_text = "Departures - Line " + demo_line + "\n\n"

        for departure in demo_departures:
            departure_text += (
                departure[0] + " "
                + departure[1] + " "
                + departure[2] + "\n"
            )

        self.tile2_label = lv.label(self.tile2)
        self.tile2_label.set_text(departure_text + "\n\n\n\n<< Swipe >>")
        self.tile2_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile2_label.center()
        self.apply_tile_colors(self.tile2, self.tile2_label, False)
        self.tile2.add_flag(lv.obj.FLAG.CLICKABLE)
        self.tile2.add_event_cb(
            self.on_tile_clicked, lv.EVENT.CLICKED, None
        )

        self.tile3_label = lv.label(self.tile3)
        self.tile3_label.set_text(
            "Settings\n"
            "Select Stop:\n\n\n"
            "Transport Type:\n\n\n"
            "Theme:\n\n\n"
            "<< Swipe"
        )
        self.tile3_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile3_label.center()
        self.apply_tile_colors(self.tile3, self.tile3_label, False)
        self.tile3.add_event_cb(
            self.on_tile_clicked, lv.EVENT.CLICKED, None
        )
        
        self.stop_dropdown = lv.dropdown(self.tile3)
        self.stop_dropdown.set_options(
            "Karlskrona Centralstation\n"
            "Karlskrona Lokstallarna\n"
            "Tullskolan Karlskrona\n"
            "Polhemsgatan Karlskrona\n"
            "Campus Gräsvik"
        )
        self.stop_dropdown.set_width(250)
        self.stop_dropdown.center()
        self.stop_dropdown.set_y(-80)
        self.stop_dropdown.add_event_cb(
            self.stop_changed, lv.EVENT.VALUE_CHANGED, None
        )

        self.transport_dropdown = lv.dropdown(self.tile3)
        self.transport_dropdown.set_options(
            "Bus\n"
            "Train\n"
            "Ferry\n"
            "All"
        )
        self.transport_dropdown.set_width(250)
        self.transport_dropdown.center()
        self.transport_dropdown.set_y(10)
        self.transport_dropdown.add_event_cb(
            self.transport_changed, lv.EVENT.VALUE_CHANGED, None
        )

        self.theme_dropdown = lv.dropdown(self.tile3)
        self.theme_dropdown.set_options(
            "Light\n"
            "Dark"
        )
        self.theme_dropdown.set_width(250)
        self.theme_dropdown.center()
        self.theme_dropdown.set_y(100)
        self.theme_dropdown.add_event_cb(
            self.theme_changed, lv.EVENT.VALUE_CHANGED, None
        )

    @staticmethod
    def connect_wifi():
        'Function: Connects to WiFi'
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(WIFI_SSID, WIFI_PASSWORD)
        started = time.ticks_ms()
        while (not station.isconnected() and
               time.ticks_diff(time.ticks_ms(), started) < 15_000):
            time.sleep_ms(250)
        log("Wi-Fi connected" if station.isconnected()
            else "Wi-Fi could not connect (timeout)")


try:
    app = Application()
except Exception as error:
    log("FATAL: %r" % (error,))
    sys.print_exception(error)
    raise
