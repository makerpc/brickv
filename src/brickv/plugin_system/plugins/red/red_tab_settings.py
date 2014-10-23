# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

red_tab_settings.py: RED settings tab implementation

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import json
import time
from PyQt4 import Qt, QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.plugin_system.plugins.red.script_manager import ScriptManager

from brickv.async_call import async_call

MANAGER_SETTINGS_CONF_PATH = "/etc/wicd/manager-settings.conf"
WIRELESS_SETTINGS_CONF_PATH = "/etc/wicd/wireless-settings.conf"
WIRED_SETTINGS_CONF_PATH = "/etc/wicd/wired-settings.conf"
BRICKD_CONF_PATH = "/etc/brickd.conf"

BOX_INDEX_NETWORK = 0
BOX_INDEX_BRICKD = 1
BOX_INDEX_DATETIME = 2
TAB_INDEX_NETWORK_GENERAL = 0
TAB_INDEX_NETWORK_WIRELESS = 1
TAB_INDEX_NETWORK_WIRED = 2
TAB_INDEX_BRICKD_GENERAL = 0
TAB_INDEX_BRICKD_ADVANCED = 1
TAB_INDEX_DATETIME_GENERAL = 0
CBOX_NET_CONTYPE_INDEX_DHCP = 0
CBOX_NET_CONTYPE_INDEX_STATIC = 1
CBOX_BRICKD_LOG_LEVEL_ERROR = 0
CBOX_BRICKD_LOG_LEVEL_WARN = 1
CBOX_BRICKD_LOG_LEVEL_INFO = 2
CBOX_BRICKD_LOG_LEVEL_DEBUG = 3
CBOX_BRICKD_LED_TRIGGER_CPU = 0
CBOX_BRICKD_LED_TRIGGER_GPIO = 1
CBOX_BRICKD_LED_TRIGGER_HEARTBEAT = 2
CBOX_BRICKD_LED_TRIGGER_MMC = 3
CBOX_BRICKD_LED_TRIGGER_OFF = 4
CBOX_BRICKD_LED_TRIGGER_ON = 5

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    script_manager = None
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None

        self.time_refresh_timer = QtCore.QTimer()
        self.time_refresh_timer.setInterval(1000)
        self.time_refresh_timer.timeout.connect(self.time_refresh)
        
        self.time_local_old = 0
        self.time_red_old = 0

        self.last_index = -1

        self.net_manager_settings_conf_rfile = None
        self.net_wired_settings_conf_rfile = None
        self.net_wireless_settings_conf_rfile = None
        self.brickd_conf_rfile = None

        self.network_all_data = {'status': None,
                             'interfaces': None,
                             'scan_result': None,
                             'manager_settings': None,
                             'wireless_settings': None,
                             'wired_settings': None}
        self.brickd_conf = {}

        self.mbox_settings = QtGui.QMessageBox()

        self.cbox_net_wired_conftype.addItem("DHCP")
        self.cbox_net_wired_conftype.addItem("Static")
        self.cbox_net_wireless_conftype.addItem("DHCP")
        self.cbox_net_wireless_conftype.addItem("Static")
        self.cbox_net_wireless_enctype.addItem("WPA 1/2 (Hex [0-9/A-F])")
        self.cbox_brickd_adv_ll.addItem("Error")
        self.cbox_brickd_adv_ll.addItem("Warn")
        self.cbox_brickd_adv_ll.addItem("Info")
        self.cbox_brickd_adv_ll.addItem("Debug")
        self.cbox_brickd_adv_rt.addItem("cpu")
        self.cbox_brickd_adv_rt.addItem("gpio")
        self.cbox_brickd_adv_rt.addItem("heartbeat")
        self.cbox_brickd_adv_rt.addItem("mmc")
        self.cbox_brickd_adv_rt.addItem("off")
        self.cbox_brickd_adv_rt.addItem("on")
        self.cbox_brickd_adv_gt.addItem("cpu")
        self.cbox_brickd_adv_gt.addItem("gpio")
        self.cbox_brickd_adv_gt.addItem("heartbeat")
        self.cbox_brickd_adv_gt.addItem("mmc")
        self.cbox_brickd_adv_gt.addItem("off")
        self.cbox_brickd_adv_gt.addItem("on")

        # Signals and slots

        # Tabs
        self.tbox_settings.currentChanged.connect(self.slot_tbox_settings_current_changed)
        self.twidget_net.currentChanged.connect(self.slot_twidget_net_current_changed)

        # Network Buttons
        self.pbutton_net_gen_save.clicked.connect(self.slot_network_general_save_clicked)
        self.pbutton_net_wireless_save.clicked.connect(self.slot_network_wireless_save_clicked)
        self.pbutton_net_wired_save.clicked.connect(self.slot_network_wired_save_clicked)
        self.pbutton_net_gen_refresh.clicked.connect(self.slot_network_refresh_clicked)
        self.pbutton_net_wireless_refresh.clicked.connect(self.slot_network_refresh_clicked)
        self.pbutton_net_wired_refresh.clicked.connect(self.slot_network_refresh_clicked)
        
        # Network fields
        self.ledit_net_gen_hostname.textEdited.connect(self.slot_network_settings_changed)
        self.cbox_net_wireless_intf.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wireless_conftype.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wireless_ap.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wireless_enctype.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.ledit_net_wireless_key.textEdited.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_ip1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_ip2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_ip3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_ip4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_mask1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_mask2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_mask3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_mask4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_gw1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_gw2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_gw3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_gw4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wireless_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wired_intf.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wired_conftype.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_ip1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_ip2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_ip3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_ip4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_mask1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_mask2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_mask3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_mask4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_gw1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_gw2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_gw3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_gw4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_dns2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_dns3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_wired_dns4.valueChanged.connect(self.slot_network_settings_changed)

        # Brick daemon buttons
        self.pbutton_brickd_general_save.clicked.connect(self.slot_brickd_save_clicked)
        self.pbutton_brickd_general_refresh.clicked.connect(self.slot_brickd_refresh_clicked)
        self.pbutton_brickd_adv_save.clicked.connect(self.slot_brickd_save_clicked)
        self.pbutton_brickd_adv_refresh.clicked.connect(self.slot_brickd_refresh_clicked)
        
        # Brick daemon fields
        self.sbox_brickd_la_ip1.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip2.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip3.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip4.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lp.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lwsp.valueChanged.connect(self.brickd_settings_changed)
        self.ledit_brickd_secret.textEdited.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_ll.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_rt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_gt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_adv_spi_dly.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_adv_rs485_dly.valueChanged.connect(self.brickd_settings_changed)


        # Date/Time buttons
        self.time_sync_button.pressed.connect(self.time_sync_pressed)

    def tab_on_focus(self):
        self.manager_settings_conf_rfile = REDFile(self.session)
        self.wired_settings_conf_rfile = REDFile(self.session)
        self.wireless_settings_conf_rfile = REDFile(self.session)
        self.brickd_conf_rfile = REDFile(self.session)

        index = self.tbox_settings.currentIndex()
        if index == BOX_INDEX_NETWORK:
            self.slot_network_refresh_clicked()
        elif index == BOX_INDEX_BRICKD:
            self.slot_brickd_refresh_clicked()
        elif index == BOX_INDEX_DATETIME:
            self.time_start()

    def tab_off_focus(self):
        index = self.tbox_settings.currentIndex()
        if index == BOX_INDEX_BRICKD:
            pass
        elif index == BOX_INDEX_NETWORK:
            pass
        elif index == BOX_INDEX_DATETIME:
            self.time_stop()

    def update_network_widget_data(self):
        if self.network_all_data['status'] is not None:
            self.ledit_net_gen_hostname.setText\
                (self.network_all_data['status']['cstat_hostname'])

            if self.network_all_data['status']['cstat_intf_active']['name'] is not None:
                self.label_net_gen_cstat_intf.setText(self.network_all_data['status']['cstat_intf_active']['name'])
                self.label_net_gen_cstat_ip.setText(self.network_all_data['status']['cstat_intf_active']['ip'])
                self.label_net_gen_cstat_mask.setText(self.network_all_data['status']['cstat_intf_active']['mask'])
            else:
                self.label_net_gen_cstat_intf.setText("Not Connected")
                self.label_net_gen_cstat_ip.setText("None")
                self.label_net_gen_cstat_mask.setText("None")

            if self.network_all_data['status']['cstat_gateway'] is not None:
                self.label_net_gen_cstat_gateway.setText(self.network_all_data['status']['cstat_gateway'])
            else:
                self.label_net_gen_cstat_gateway.setText("None")
            
            if self.network_all_data['status']['cstat_dns'] is not None:
                self.label_net_gen_cstat_dns.setText(self.network_all_data['status']['cstat_dns'].strip())
            else:
                self.label_net_gen_cstat_dns.setText("None")
        else:
            self.ledit_net_gen_hostname.setText("None")
            self.label_net_gen_cstat_intf.setText("None")
            self.label_net_gen_cstat_ip.setText("None")
            self.label_net_gen_cstat_mask.setText("None")
            self.label_net_gen_cstat_gateway.setText("None")
            self.label_net_gen_cstat_dns.setText("None")

        if self.network_all_data['interfaces'] is not None:
            if self.network_all_data['interfaces']['wireless'] is not None:
                self.cbox_net_wireless_intf.clear()
                for wintf in self.network_all_data['interfaces']['wireless']:
                    self.cbox_net_wireless_intf.addItem(wintf)

            if self.network_all_data['interfaces']['wired'] is not None:
                self.cbox_net_wired_intf.clear()
                for wintf in self.network_all_data['interfaces']['wired']:
                    self.cbox_net_wired_intf.addItem(wintf)
            if self.network_all_data['manager_settings'] is not None:
                try:
                    _wiredintf = self.network_all_data['manager_settings'].get('Settings', 'wired_interface')
                    if _wiredintf == "" or _wiredintf is None:
                        pass
                    else:
                        for i in range(self.cbox_net_wired_intf.count()):
                            if self.cbox_net_wired_intf.itemText(i) == _wiredintf:
                                self.cbox_net_wired_intf.setCurrentIndex(i)
                                break
                except:
                    pass
            
        if self.network_all_data['wireless_settings'] is not None:
            pass

        if self.network_all_data['wired_settings'] is not None:
            try:
                _ips = self.network_all_data['wired_settings'].get('wired-default', 'ip')
                if _ips == "None" or _ips == "":
                    self.cbox_net_wired_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
                    self.sbox_net_wired_ip1.setValue(0)
                    self.sbox_net_wired_ip2.setValue(0)
                    self.sbox_net_wired_ip3.setValue(0)
                    self.sbox_net_wired_ip4.setValue(0)
                else:
                    self.cbox_net_wired_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_STATIC)
                    _ips_splitted = _ips.split('.')
                    self.sbox_net_wired_ip1.setValue(int(_ips_splitted[0]))
                    self.sbox_net_wired_ip2.setValue(int(_ips_splitted[1]))
                    self.sbox_net_wired_ip3.setValue(int(_ips_splitted[2]))
                    self.sbox_net_wired_ip4.setValue(int(_ips_splitted[3]))
            except:
                self.cbox_net_wired_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
                self.sbox_net_wired_ip1.setValue(0)
                self.sbox_net_wired_ip2.setValue(0)
                self.sbox_net_wired_ip3.setValue(0)
                self.sbox_net_wired_ip4.setValue(0)
            try:
                _mask = self.network_all_data['wired_settings'].get('wired-default', 'netmask')
                if _ips == "None" or _ips == "":
                    self.sbox_net_wired_mask1.setValue(0)
                    self.sbox_net_wired_mask2.setValue(0)
                    self.sbox_net_wired_mask3.setValue(0)
                    self.sbox_net_wired_mask4.setValue(0)
                else:
                    _mask_splitted = _mask.split('.')
                    self.sbox_net_wired_mask1.setValue(int(_mask_splitted[0]))
                    self.sbox_net_wired_mask2.setValue(int(_mask_splitted[1]))
                    self.sbox_net_wired_mask3.setValue(int(_mask_splitted[2]))
                    self.sbox_net_wired_mask4.setValue(int(_mask_splitted[3]))
            except:
                self.sbox_net_wired_mask1.setValue(0)
                self.sbox_net_wired_mask2.setValue(0)
                self.sbox_net_wired_mask3.setValue(0)
                self.sbox_net_wired_mask4.setValue(0)

            try:
                _gw = self.network_all_data['wired_settings'].get('wired-default', 'gateway')
                if _gw == "None" or _gw == "":
                    self.sbox_net_wired_gw1.setValue(0)
                    self.sbox_net_wired_gw2.setValue(0)
                    self.sbox_net_wired_gw3.setValue(0)
                    self.sbox_net_wired_gw4.setValue(0)
                else:
                    _gw_splitted = _gw.split('.')
                    self.sbox_net_wired_gw1.setValue(int(_gw_splitted[0]))
                    self.sbox_net_wired_gw2.setValue(int(_gw_splitted[1]))
                    self.sbox_net_wired_gw3.setValue(int(_gw_splitted[2]))
                    self.sbox_net_wired_gw4.setValue(int(_gw_splitted[3]))
            except:
                self.sbox_net_wired_gw1.setValue(0)
                self.sbox_net_wired_gw2.setValue(0)
                self.sbox_net_wired_gw3.setValue(0)
                self.sbox_net_wired_gw4.setValue(0)

            try:
                _dns = self.network_all_data['wired_settings'].get('wired-default', 'dns1')
                if _dns == "None" or _dns == "":
                    self.sbox_net_wired_dns1.setValue(0)
                    self.sbox_net_wired_dns2.setValue(0)
                    self.sbox_net_wired_dns3.setValue(0)
                    self.sbox_net_wired_dns4.setValue(0)
                else:
                    _dns_splitted = _dns.split('.')
                    self.sbox_net_wired_dns1.setValue(int(_dns_splitted[0]))
                    self.sbox_net_wired_dns2.setValue(int(_dns_splitted[1]))
                    self.sbox_net_wired_dns3.setValue(int(_dns_splitted[2]))
                    self.sbox_net_wired_dns4.setValue(int(_dns_splitted[3]))
            except:
                self.sbox_net_wired_dns1.setValue(0)
                self.sbox_net_wired_dns2.setValue(0)
                self.sbox_net_wired_dns3.setValue(0)
                self.sbox_net_wired_dns4.setValue(0)

    def update_brickd_widget_data(self):
        if self.brickd_conf == None:
            return

        # Fill keys with default values if not available
        if not 'listen.address' in self.brickd_conf:
            self.brickd_conf['listen.address'] = '0.0.0.0'
        if not 'listen.plain_port' in self.brickd_conf:
            self.brickd_conf['listen.plain_port'] = '4223'
        if not 'listen.websocket_port' in self.brickd_conf:
            self.brickd_conf['listen.websocket_port'] = '0'
        if not 'authentication.secret' in self.brickd_conf:
            self.brickd_conf['authentication.secret'] = ''
        if not 'log_level.event' in self.brickd_conf:
            self.brickd_conf['log_level.event'] = 'info'
        if not 'log_level.usb' in self.brickd_conf:
            self.brickd_conf['log_level.usb'] = 'info'
        if not 'log_level.network' in self.brickd_conf:
            self.brickd_conf['log_level.network'] = 'info'
        if not 'log_level.hotplug' in self.brickd_conf:
            self.brickd_conf['log_level.hotplug'] = 'info'
        if not 'log_level.hardware' in self.brickd_conf:
            self.brickd_conf['log_level.hardware'] = 'info'
        if not 'log_level.websocket' in self.brickd_conf:
            self.brickd_conf['log_level.websocket'] = 'info'
        if not 'log_level.red_brick' in self.brickd_conf:
            self.brickd_conf['log_level.red_brick'] = 'info'
        if not 'log_level.spi' in self.brickd_conf:
            self.brickd_conf['log_level.spi'] = 'info'
        if not 'log_level.rs485' in self.brickd_conf:
            self.brickd_conf['log_level.rs485'] = 'info'
        if not 'log_level.other' in self.brickd_conf:
            self.brickd_conf['log_level.other'] = 'info'
        if not 'led_trigger.green' in self.brickd_conf:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        if not 'led_trigger.red' in self.brickd_conf:
            self.brickd_conf['led_trigger.red'] = 'off'
        if not 'poll_delay.spi' in self.brickd_conf:
            self.brickd_conf['poll_delay.spi'] = '50'
        if not 'poll_delay.rs485' in self.brickd_conf:
            self.brickd_conf['poll_delay.rs485'] = '4000'

        l_addr = self.brickd_conf['listen.address'].split('.')
        self.sbox_brickd_la_ip1.setValue(int(l_addr[0]))
        self.sbox_brickd_la_ip2.setValue(int(l_addr[1]))
        self.sbox_brickd_la_ip3.setValue(int(l_addr[2]))
        self.sbox_brickd_la_ip4.setValue(int(l_addr[3]))
        
        self.sbox_brickd_lp.setValue(int(self.brickd_conf['listen.plain_port']))
        self.sbox_brickd_lwsp.setValue(int(self.brickd_conf['listen.websocket_port']))
        self.ledit_brickd_secret.setText(self.brickd_conf['authentication.secret'])
        
        log_level = self.brickd_conf['log_level.other']
        if log_level == 'debug':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_DEBUG)
        elif log_level == 'info':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_INFO)
        elif log_level == 'warn':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_WARN)
        elif log_level == 'error':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_ERROR)
        
        trigger_green = self.brickd_conf['led_trigger.green']
        if trigger_green == 'cpu':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_green == 'gpio':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_green == 'heartbeat':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_green == 'mmc':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_green == 'off':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_green == 'on':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)
            
        trigger_red = self.brickd_conf['led_trigger.red']
        if trigger_red == 'cpu':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_red == 'gpio':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_red == 'heartbeat':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_red == 'mmc':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_red == 'off':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_red == 'on':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)
        
        self.sbox_brickd_adv_spi_dly.setValue(int(self.brickd_conf['poll_delay.spi']))
        self.sbox_brickd_adv_rs485_dly.setValue(int(self.brickd_conf['poll_delay.rs485']))

    def update_datetime_widget_data(self):
        pass

    def network_show_hide_static_ipconf(self, tidx, contype):
        if tidx == TAB_INDEX_NETWORK_WIRELESS:
            if contype == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_net_wireless_staticipconf.hide()
            elif contype == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_net_wireless_staticipconf.show()

        elif tidx == TAB_INDEX_NETWORK_WIRED:
            if contype == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_net_wired_staticipconf.hide()
            elif contype == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_net_wired_staticipconf.show()

    # The slots
    def slot_tbox_settings_current_changed(self, ctidx):
        if self.last_index == BOX_INDEX_BRICKD:
            pass
        elif self.last_index == BOX_INDEX_NETWORK:
            pass
        elif self.last_index == BOX_INDEX_DATETIME:
            self.time_stop()
            
        self.last_index = ctidx

        if ctidx == BOX_INDEX_NETWORK:
            self.slot_network_refresh_clicked()

            if self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRELESS:
                self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRELESS,
                                                     self.cbox_net_wireless_conftype.currentIndex())

            elif self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRED:
                self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRED,
                                                     self.cbox_net_wired_conftype.currentIndex())

        elif ctidx == BOX_INDEX_BRICKD:
            self.slot_brickd_refresh_clicked()
        elif self.last_index == BOX_INDEX_DATETIME:
            self.time_start()

    def slot_twidget_net_current_changed(self, ctidx):
        if self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRELESS:
            self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRELESS,
                                                 self.cbox_net_wireless_conftype.currentIndex())
            
        elif self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRED:
            self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRED,
                                                 self.cbox_net_wired_conftype.currentIndex())

    def network_button_refresh_enabled(self, state):
        self.pbutton_net_gen_refresh.setEnabled(state)
        self.pbutton_net_wireless_refresh.setEnabled(state)
        self.pbutton_net_wired_refresh.setEnabled(state)

        if state:
            self.pbutton_net_gen_refresh.setText("Refresh")
            self.pbutton_net_wireless_refresh.setText("Refresh")
            self.pbutton_net_wired_refresh.setText("Refresh")
        else:
            self.pbutton_net_gen_refresh.setText("Refreshing...")
            self.pbutton_net_wireless_refresh.setText("Refreshing...")
            self.pbutton_net_wired_refresh.setText("Refreshing...")

    def network_button_save_enabled(self, state):
        self.pbutton_net_gen_save.setEnabled(state)
        self.pbutton_net_wireless_save.setEnabled(state)
        self.pbutton_net_wired_save.setEnabled(state)

        if state:
            self.pbutton_net_gen_save.setText("Save")
            self.pbutton_net_wireless_save.setText("Save")
            self.pbutton_net_wired_save.setText("Save")
        else:
            self.pbutton_net_gen_save.setText("Saved")
            self.pbutton_net_wireless_save.setText("Saved")
            self.pbutton_net_wired_save.setText("Saved")

    def brickd_button_refresh_enabled(self, state):
        self.pbutton_brickd_general_refresh.setEnabled(state)
        self.pbutton_brickd_adv_refresh.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_refresh.setText("Refresh")
            self.pbutton_brickd_adv_refresh.setText("Refresh")
        else:
            self.pbutton_brickd_general_refresh.setText("Refreshing...")
            self.pbutton_brickd_adv_refresh.setText("Refreshing...")
        
    
    def brickd_button_save_enabled(self, state):
        self.pbutton_brickd_general_save.setEnabled(state)
        self.pbutton_brickd_adv_save.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_save.setText("Save")
            self.pbutton_brickd_adv_save.setText("Save")
        else:
            self.pbutton_brickd_general_save.setText("Saved")
            self.pbutton_brickd_adv_save.setText("Saved")

    def slot_network_refresh_clicked(self):
        self.network_button_refresh_enabled(False)

        def cb_settings_network_status(result):
            if result.stderr == "":
                self.network_all_data['status'] = json.loads(result.stdout)
                self.update_network_widget_data()
            else:
                pass
                # TODO: Error popup for user?

            self.network_button_refresh_enabled(True)
            self.network_button_save_enabled(False)

        def cb_settings_network_get_interfaces(result):
            if result.stderr == "":
                self.network_all_data['interfaces'] = json.loads(result.stdout)
                self.update_network_widget_data()
            else:
                pass
                # TODO: Error popup for user?

            self.network_button_refresh_enabled(True)
            self.network_button_save_enabled(False)

        def cb_settings_network_wireless_scan(result):
            if result.stderr == "":
                _srdict = {}
                _lines = result.stdout.split('\n')
                for l in _lines:
                    lsplitted = l.split('\t')
                    if len(lsplitted) == 1:
                        continue
                    _idx = lsplitted[3] # 0 = ESSID, 1 = BSSID, 2 = Channel 3 = Index
                    lsplitted.pop() # Getting rid of the last item
                    _srdict[_idx] = lsplitted
                self.network_all_data['scan_result'] = _srdict
                self.update_network_widget_data()
            else:
                pass
                # TODO: Error popup for user?

            self.network_button_refresh_enabled(True)
            self.network_button_save_enabled(False)

        def cb_open_manager_settings(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.network_all_data['manager_settings'] = config_parser.parse_no_fake(result.data)
                    self.update_network_widget_data()
                else:
                    # TODO: Error popup for user?
                    print result

                self.network_button_refresh_enabled(True)
                self.network_button_save_enabled(False)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_manager_settings(result):
            self.network_button_refresh_enabled(True)
            # TODO: Error popup for user?
            print result

        def cb_open_wireless_settings(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.network_all_data['wireless_settings'] = config_parser.parse_no_fake(result.data)
                    self.update_network_widget_data()
                else:
                    # TODO: Error popup for user?
                    print result

                self.network_button_refresh_enabled(True)
                self.network_button_save_enabled(False)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_wireless_settings(result):
            self.network_button_refresh_enabled(True)
            # TODO: Error popup for user?
            print result

        def cb_open_wired_settings(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.network_all_data['wired_settings'] = config_parser.parse_no_fake(result.data)
                    self.update_network_widget_data()
                else:
                    # TODO: Error popup for user?
                    print result

                self.network_button_refresh_enabled(True)
                self.network_button_save_enabled(False)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_wired_settings(result):
            self.network_button_refresh_enabled(True)
            # TODO: Error popup for user?
            print result

        self.script_manager.execute_script('settings_network_status',
                                           cb_settings_network_status,
                                           [])

        self.script_manager.execute_script('settings_network_get_interfaces',
                                           cb_settings_network_get_interfaces,
                                           [])

        self.script_manager.execute_script('settings_network_wireless_scan',
                                           cb_settings_network_wireless_scan,
                                           ['cache'])

        async_call(self.manager_settings_conf_rfile.open,
                   (MANAGER_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_manager_settings,
                   cb_open_error_manager_settings)

        async_call(self.wireless_settings_conf_rfile.open,
                   (WIRELESS_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_wireless_settings,
                   cb_open_error_wireless_settings)

        async_call(self.wired_settings_conf_rfile.open,
                   (WIRED_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_wired_settings,
                   cb_open_error_wired_settings)

    def slot_brickd_refresh_clicked(self):
        self.brickd_button_refresh_enabled(False)

        def cb_open(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.brickd_conf = config_parser.parse(result.data)
                    self.update_brickd_widget_data()
                else:
                    # TODO: Error popup for user?
                    print result

                self.brickd_button_refresh_enabled(True)
                self.brickd_button_save_enabled(False)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error(result):
            self.brickd_button_refresh_enabled(True)
            
            # TODO: Error popup for user?
            print result

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open,
                   cb_open_error)

    def slot_network_save_clicked(self):
        self.network_button_save_enabled(False)
        pass

    def slot_network_general_save_clicked(self):
        self.network_button_save_enabled(False)
        pass
        
    def slot_network_wireless_save_clicked(self):
        self.network_button_save_enabled(False)
        pass
        
    def slot_network_wired_save_clicked(self):
        self.network_button_save_enabled(False)
        
        def cb_settings_network_apply_wired(result):
            print result
            if result.stderr is not None and  result.stderr == "":
                pass
            else:
                # TODO: Error popup for user?
                pass

        self.network_all_data['manager_settings'].set('Settings', 'wired_interface', self.cbox_net_wired_intf.currentText())
        config_ms = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])

        idx = self.cbox_net_wired_conftype.currentIndex()
        if idx == CBOX_NET_CONTYPE_INDEX_DHCP:
            self.network_all_data['wired_settings'].set('wired-default', 'ip', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'broadcast', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'netmask', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'gateway', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'search_domain', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns_domain', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns1', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns2', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns3', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'default', 'True')
            
            config = config_parser.to_string_no_fake(self.network_all_data['wired_settings'])

            def cb_open(config, red_file):
                def cb_write(red_file, result):
                    red_file.release()

                    if result is not None:
                        self.network_button_save_enabled(True)
                        # TODO: Error popup for user?
                        print result
                    else:
                        self.script_manager.execute_script('settings_network_apply_wired',
                                                           cb_settings_network_apply_wired,
                                                           [])
                
                red_file.write_async(config, lambda x: cb_write(red_file, x), None)
            
            def cb_open_error(result):
                self.brickd_button_save_enabled(True)
            
                # TODO: Error popup for user?
                print result

            async_call(self.wired_settings_conf_rfile.open,
                       (WIRED_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                       lambda x: cb_open(config, x),
                       cb_open_error)

        elif idx == CBOX_NET_CONTYPE_INDEX_STATIC:
            ip = '.'.join((str(self.sbox_net_wired_ip1.value()),
                           str(self.sbox_net_wired_ip2.value()),
                           str(self.sbox_net_wired_ip3.value()),
                           str(self.sbox_net_wired_ip4.value())))

            mask = '.'.join((str(self.sbox_net_wired_mask1.value()),
                             str(self.sbox_net_wired_mask2.value()),
                             str(self.sbox_net_wired_mask3.value()),
                             str(self.sbox_net_wired_mask4.value())))

            gw = '.'.join((str(self.sbox_net_wired_gw1.value()),
                           str(self.sbox_net_wired_gw2.value()),
                           str(self.sbox_net_wired_gw3.value()),
                           str(self.sbox_net_wired_gw4.value())))

            dns = '.'.join((str(self.sbox_net_wired_dns1.value()),
                            str(self.sbox_net_wired_dns2.value()),
                            str(self.sbox_net_wired_dns3.value()),
                            str(self.sbox_net_wired_dns4.value())))

            self.network_all_data['wired_settings'].set('wired-default', 'ip', ip)
            self.network_all_data['wired_settings'].set('wired-default', 'broadcast', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'netmask', mask)
            self.network_all_data['wired_settings'].set('wired-default', 'gateway', gw)
            self.network_all_data['wired_settings'].set('wired-default', 'search_domain', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns_domain', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns1', dns)
            self.network_all_data['wired_settings'].set('wired-default', 'dns2', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'dns3', 'None')
            self.network_all_data['wired_settings'].set('wired-default', 'default', 'True')

            config = config_parser.to_string_no_fake(self.network_all_data['wired_settings'])

            def cb_open(config, red_file):
                def cb_write(red_file, result):
                    red_file.release()

                    if result is not None:
                        self.network_button_save_enabled(True)
                        # TODO: Error popup for user?
                        print result
                    else:
                        self.script_manager.execute_script('settings_network_apply_wired',
                                                           cb_settings_network_apply_wired,
                                                           [])
                
                red_file.write_async(config, lambda x: cb_write(red_file, x), None)
            
            def cb_open_error(result):
                self.brickd_button_save_enabled(True)
                # TODO: Error popup for user?
                print result

            async_call(self.wired_settings_conf_rfile.open,
                       (WIRED_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                       lambda x: cb_open(config, x),
                       cb_open_error)

        def cb_open_ms(config, red_file):
            def cb_write_ms(red_file, result):
                red_file.release()

                if result is not None:
                    self.network_button_save_enabled(True)
                    # TODO: Error popup for user?
                    print result
                else:
                    self.script_manager.execute_script('settings_network_apply_wired',
                                                       cb_settings_network_apply_wired,
                                                       [])
                
            red_file.write_async(config_ms, lambda x: cb_write_ms(red_file, x), None)

        def cb_open_ms_error(result):
            self.brickd_button_save_enabled(True)
            # TODO: Error popup for user?
            print result

        async_call(self.manager_settings_conf_rfile.open,
                   (MANAGER_SETTINGS_CONF_PATH,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                   lambda x: cb_open_ms(config, x),
                   cb_open_ms_error)

    def slot_brickd_save_clicked(self):
        self.brickd_button_save_enabled(False)

        # General
        adr = '.'.join((str(self.sbox_brickd_la_ip1.value()),
                        str(self.sbox_brickd_la_ip2.value()),
                        str(self.sbox_brickd_la_ip3.value()),
                        str(self.sbox_brickd_la_ip4.value())))
        self.brickd_conf['listen.address'] = adr
        self.brickd_conf['listen.plain_port'] = str(self.sbox_brickd_lp.value())
        self.brickd_conf['listen.websocket_port'] = str(self.sbox_brickd_lwsp.value())
        self.brickd_conf['authentication.secret'] = str(self.ledit_brickd_secret.text())
        
        def set_all_log_level(level):
            self.brickd_conf['log_level.event'] = level
            self.brickd_conf['log_level.usb'] = level
            self.brickd_conf['log_level.network'] = level
            self.brickd_conf['log_level.hotplug'] = level
            self.brickd_conf['log_level.hardware'] = level
            self.brickd_conf['log_level.websocket'] = level
            self.brickd_conf['log_level.red_brick'] = level
            self.brickd_conf['log_level.spi'] = level
            self.brickd_conf['log_level.rs485'] = level
            self.brickd_conf['log_level.other'] = level            
        
        # Advanced
        index = self.cbox_brickd_adv_ll.currentIndex()
        if index == CBOX_BRICKD_LOG_LEVEL_ERROR:
            set_all_log_level('error')
        elif index == CBOX_BRICKD_LOG_LEVEL_WARN:
            set_all_log_level('warn')
        elif index == CBOX_BRICKD_LOG_LEVEL_INFO:
            set_all_log_level('info')
        elif index == CBOX_BRICKD_LOG_LEVEL_DEBUG:
            set_all_log_level('debug')
            
        index = self.cbox_brickd_adv_gt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.green'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.green'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.green'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.green'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
            self.brickd_conf['led_trigger.green'] = 'on'
        
        index = self.cbox_brickd_adv_rt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.red'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.red'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.red'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.red'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.red'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
            self.brickd_conf['led_trigger.red'] = 'on'
            
        self.brickd_conf['poll_delay.spi'] = str(self.sbox_brickd_adv_spi_dly.value())
        self.brickd_conf['poll_delay.rs485'] = str(self.sbox_brickd_adv_rs485_dly.value())
        
        config = config_parser.to_string(self.brickd_conf)

        def cb_open(config, red_file):
            def cb_write(red_file, result):
                red_file.release()

                if result is not None:
                    self.brickd_button_save_enabled(True)
                    # TODO: Error popup for user?
                    print result
                else:
                    self.script_manager.execute_script('restart_brickd', None)
                    QtGui.QMessageBox.information(None, 'Configuration', 'Saved configuration successfully, restarting brickd.', QtGui.QMessageBox.Ok)

                
            red_file.write_async(config, lambda x: cb_write(red_file, x), None)
            
        def cb_open_error(result):
            self.brickd_button_save_enabled(True)
            
            # TODO: Error popup for user?
            print result

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                   lambda x: cb_open(config, x),
                   cb_open_error)

    def slot_network_settings_changed(self):
        self.network_button_save_enabled(True)

        if self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRELESS:
            self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRELESS,
                                                 self.cbox_net_wireless_conftype.currentIndex())

        elif self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_WIRED:
            self.network_show_hide_static_ipconf(TAB_INDEX_NETWORK_WIRED,
                                                 self.cbox_net_wired_conftype.currentIndex())

    def brickd_settings_changed(self, value):
        self.brickd_button_save_enabled(True)



    # ======== date/time settings =========
    
    def time_utc_offset(self):
        if time.localtime(time.time()).tm_isdst and time.daylight:
            return -time.altzone/(60*60)
        
        return -time.timezone/(60*60)
    
    def time_start(self):
        self.time_sync_button.setEnabled(False)

        def cb_red_brick_time(result):
            try:
                if result.stderr == '':
                    self.time_red_old, tz = map(int, result.stdout.split('\n')[:2])
                    if tz < 0:
                        tz_str_red = "UTC" + str(tz)
                    else:
                        tz_str_red = "UTC+" + str(tz)
                    self.time_timezone_red.setText(tz_str_red)
                    
                    self.time_local_old = int(time.time())
                    tz = self.time_utc_offset()
                    if tz < 0:
                        tz_str_local = "UTC" + str(tz)
                    else:
                        tz_str_local = "UTC+" + str(tz)
                    
                    self.time_timezone_local.setText(tz_str_local)
                    self.time_update_gui()
                    
                    self.time_refresh_timer.start()
                    
                    if (self.time_red_old == self.time_local_old) and (tz_str_local == tz_str_red):
                        self.time_sync_button.setEnabled(False)
                    else:
                        self.time_sync_button.setEnabled(True)
                        
                    return
                else:
                    # TODO: Error popup for user?
                    print result.stderr
            except:
                # TODO: Error popup for user?
                traceback.print_exc()
            
            self.time_sync_button.setEnabled(True)
        
        self.script_manager.execute_script('settings_time_get',
                                           cb_red_brick_time,
                                           [])
    
    def time_stop(self):
        try:
            self.time_refresh_timer.stop()
        except:
            traceback.print_exc()
            
    def time_refresh(self):
        self.time_local_old += 1
        self.time_red_old += 1
        
        self.time_update_gui()
        
    def time_update_gui(self):
        t = QtCore.QDateTime.fromTime_t(self.time_local_old)
        self.time_date_local.setDateTime(t)
        self.time_time_local.setDateTime(t)
        
        t = QtCore.QDateTime.fromTime_t(self.time_red_old)
        self.time_date_red.setDateTime(t)
        self.time_time_red.setDateTime(t)
        
    def time_sync_pressed(self):
        def state_changed(process, t, p):
            if p.state == REDProcess.STATE_ERROR:
                # TODO: Error popup for user?
                process.release()
            elif p.state == REDProcess.STATE_EXITED:
                if t == 0: #timezone
                    self.time_timezone_red.setText(self.time_timezone_local.text())
                elif t == 1: #time
                    self.time_red_old = self.time_local_old
                    
                process.release()
                
            if (self.time_red_old == self.time_local_old) and (self.time_timezone_red.text() == self.time_timezone_local.text()):
                self.time_sync_button.setEnabled(False)
            else:
                self.time_sync_button.setEnabled(True)
            
        tz = -self.time_utc_offset() # Use posix timezone definition
        if tz < 0:
            tz_str = str(tz)
        else:
            tz_str = '+' + str(tz)
            
        set_tz_str = ('/bin/ln -sf /usr/share/zoneinfo/Etc/GMT' + tz_str + ' /etc/localtime').split(' ')
        red_process_tz = REDProcess(self.session)
        red_process_tz.state_changed_callback = lambda x: state_changed(red_process_tz, 0, x)
        red_process_tz.spawn(set_tz_str[0], set_tz_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

        set_t_str = ('/bin/date +%s -u -s @' + str(int(time.time()))).split(' ')
        red_process_t = REDProcess(self.session)
        red_process_t.state_changed_callback = lambda x: state_changed(red_process_t, 1, x)
        red_process_t.spawn(set_t_str[0], set_t_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

