# -*- coding: utf-8 -*-  
"""
Solid State Relay Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

solid_state_relay.py: Solid State Relay Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_solid_state_relay import BrickletSolidStateRelay
from brickv.async_call import async_call

from PyQt4.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.plugins.solid_state_relay.ui_solid_state_relay import Ui_SolidStateRelay
from brickv.bmp_to_pixmap import bmp_to_pixmap

class SolidStateRelay(PluginBase, Ui_SolidStateRelay):
    qtcb_monoflop = pyqtSignal(int, bool)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Solid State Relay Bricklet', version, BrickletSolidStateRelay)
        
        self.setupUi(self)
        
        self.ssr = self.device
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.dr.register_callback(self.dr.CALLBACK_MONOFLOP_DONE,
                                  self.qtcb_monoflop.emit)
        
        self.dr_button.pressed.connect(self.dr_pressed)
        self.go_button.pressed.connect(self.go_pressed)

        self.monoflop = False
        self.timebefore = 500
        
        self.a_pixmap = bmp_to_pixmap('plugin_system/plugins/solid_state_relay/relay_a.bmp')
        self.b_pixmap = bmp_to_pixmap('plugin_system/plugins/solid_state_relay/relay_b.bmp')

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

    def get_state_async(self, state):
        s = state
        if s:
            self.dr_button.setText('Switch Off')
            self.dr_image.setPixmap(self.a_pixmap)
        else:
            self.dr_button.setText('Switch On')
            self.dr_image.setPixmap(self.b_pixmap)
            
    def get_monoflop_async(self, monoflop):
        state, time, time_remaining = monoflop
        if time > 0:
            self.timebefore = time
            self.time_spinbox.setValue(self.timebefore)
        if time_remaining > 0:
            if not state:
                self.state_combobox.setCurrentIndex(0)
            self.monoflop = True
            self.time_spinbox.setEnabled(False)
            self.state_combobox.setEnabled(False)

    def start(self):
        async_call(self.dr.get_state, None, self.get_state_async, self.increase_error_count)
        async_call(self.dr.get_monoflop, None, self.get_monoflop_async, self.increase_error_count)
        self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'solid_state_relay'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSolidStateRelay.DEVICE_IDENTIFIER

    def get_state_dr_pressed(self, state):
        try:
            self.dr.set_state(state)
        except ip_connection.Error:
            return
        
        self.monoflop = False
        self.time_spinbox.setValue(self.timebefore)
        self.time_spinbox.setEnabled(True)
        self.state_combobox.setEnabled(True)
        
    def dr_pressed(self):
        if 'On' in self.dr_button.text():
            self.dr_button.setText('Switch Off')
            self.dr_image.setPixmap(self.a_pixmap)
        else:
            self.dr_button.setText('Switch On')
            self.dr_image.setPixmap(self.b_pixmap)

        async_call(self.dr.get_state, None, self.get_state_dr_pressed, self.increase_error_count)

    def go_pressed(self):   
        time = self.time_spinbox.value()
        state = self.state_combobox.currentIndex() == 0
        try:
            if self.monoflop:
                time = self.timebefore
            else:
                self.timebefore = self.time_spinbox.value()
                
            self.dr.set_monoflop(state, time)
            
            self.monoflop = True
            self.time_spinbox.setEnabled(False)
            self.state_combobox.setEnabled(False)
            
            if state:
                self.dr_button.setText('Switch Off')
                self.dr_image.setPixmap(self.a_pixmap)
            else:
                self.dr_button.setText('Switch On')
                self.dr_image.setPixmap(self.b_pixmap)
        except ip_connection.Error:
            return

    def cb_monoflop(self, state):
        self.monoflop = False
        self.time_spinbox.setValue(self.timebefore)
        self.time_spinbox.setEnabled(True)
        self.state_combobox.setEnabled(True)
        if state:
            self.dr_button.setText('Switch Off')
            self.dr_image.setPixmap(self.a_pixmap)
        else:
            self.dr_button.setText('Switch On')
            self.dr_image.setPixmap(self.b_pixmap)
    
    def update_time_remaining(self, time_remaining):
        if self.monoflop:
            self.time_spinbox.setValue(time_remaining)

    def update(self):
        if self.monoflop:
            try:
                async_call(self.dr.get_monoflop, None, lambda a: self.update_time_remaining(a[2]), self.increase_error_count)
            except ip_connection.Error:
                pass