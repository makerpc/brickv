# -*- coding: utf-8 -*-  
"""
Industrial Digital Out 4 Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

industrial_digital_out_4.py: Industrial Digital Out 4 Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import Qt, pyqtSignal, QTimer

from ui_industrial_digital_out_4 import Ui_IndustrialDigitalOut4
from dio_gnd_pixmap import get_dio_gnd_pixmap
from dio_vcc_pixmap import get_dio_vcc_pixmap

from bindings import bricklet_industrial_digital_out_4
        
class IndustrialDigitalOut4(PluginBase, Ui_IndustrialDigitalOut4):
    qtcb_monoflop = pyqtSignal(int, int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.ido4 = bricklet_industrial_digital_out_4.IndustrialDigitalOut4(self.uid)
        self.ipcon.add_device(self.ido4)
        version = self.ido4.get_version()[1]
        self.version = '.'.join(map(str, version))
        
        self.gnd_pixmap = get_dio_gnd_pixmap()
        self.vcc_pixmap = get_dio_vcc_pixmap()
        
        self.pin_buttons = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b10, self.b11, self.b12, self.b13, self.b14, self.b15]
        self.pin_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon, self.b4_icon, self.b5_icon, self.b6_icon, self.b7_icon, self.b8_icon, self.b9_icon, self.b10_icon, self.b11_icon, self.b12_icon, self.b13_icon, self.b14_icon, self.b15_icon]
        self.pin_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label, self.b4_label, self.b5_label, self.b6_label, self.b7_label, self.b8_label, self.b9_label, self.b10_label, self.b11_label, self.b12_label, self.b13_label, self.b14_label, self.b15_label]
        self.groups = [self.group0, self.group1, self.group2, self.group3]
        for icon in self.pin_button_icons:
            icon.setPixmap(self.gnd_pixmap)
            icon.show()

        self.lines = [self.line_0vs1, self.line_1vs2, self.line_2vs3, self.line_3vs4]
        for line in self.lines:
            line.setVisible(False)
        
        self.available_ports = self.ido4.get_available_for_group()
        
        def get_button_lambda(button):
            return lambda: self.pin_button_pressed(button)
        
        for i in range(len(self.pin_buttons)):
            self.pin_buttons[i].pressed.connect(get_button_lambda(i))
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.ido4.register_callback(self.ido4.CALLBACK_MONOFLOP_DONE,
                                   self.qtcb_monoflop.emit)
        
        self.set_group.pressed.connect(self.set_group_pressed)
        
        self.monoflop_pin.currentIndexChanged.connect(self.monoflop_pin_changed)
        self.monoflop_go.pressed.connect(self.monoflop_go_pressed)
        self.monoflop_time_before = [1000] * 16
        self.monoflop_pending = [False] * 16
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        self.reconfigure_everything()

    def start(self):
        self.reconfigure_everything()

    def stop(self):
        self.update_timer.stop()

    @staticmethod
    def has_name(name):
        return 'Industrial Digital Out 4 Bricklet' in name 
    
    def reconfigure_everything(self):
        for i in range(4):
            self.groups[i].removeItem(0)
            self.groups[i].removeItem(0)
            self.groups[i].removeItem(0)
            self.groups[i].removeItem(0)
            self.groups[i].removeItem(0)
            self.groups[i].addItem('Off')
            for j in range(4):
                if self.available_ports & (1 << j):
                    item = 'Port ' + chr(ord('A') + j)
                    self.groups[i].addItem(item)
                    
        group = self.ido4.get_group()
        
        for i in range(4):
            if group[i] == 'n':
                self.groups[i].setCurrentIndex(0)
            else:
                item = 'Port ' + group[i].upper()
                index = self.groups[i].findText(item, Qt.MatchStartsWith)
                if index == -1:
                    self.groups[i].setCurrentIndex(0)
                else:
                    self.groups[i].setCurrentIndex(index)
                    
        for i in range(16):
            self.monoflop_pin.removeItem(0)
            
        if group[0] == 'n' and group[1] == 'n' and group[2] == 'n' and group[3] == 'n':
            self.show_buttons(0)
            self.hide_buttons(1)
            self.hide_buttons(2)
            self.hide_buttons(3)
            self.monoflop_pin.addItem('Pin 0')
            self.monoflop_pin.addItem('Pin 1')
            self.monoflop_pin.addItem('Pin 2')
            self.monoflop_pin.addItem('Pin 3')
        else:
            for i in range(4):
                if group[i] == 'n':
                    self.hide_buttons(i)
                else:
                    for j in range(4):
                        self.monoflop_pin.addItem('Pin ' + str(i*4+j))
                    self.show_buttons(i)

        value_mask = self.ido4.get_value()

        for pin in range(16):
            if value_mask & (1 << pin):
                self.pin_buttons[pin].setText('Switch Low')
                self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
            else:
                self.pin_buttons[pin].setText('Switch High')
                self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

            index = self.monoflop_pin.findText('Pin {0}'.format(pin))
            if index >= 0:
                value, time, time_remaining = self.ido4.get_monoflop(pin)

                if time_remaining > 0:
                    self.monoflop_pending[pin] = True
                    self.monoflop_time_before[pin] = time

                    self.monoflop_pin.setCurrentIndex(index)
                    self.monoflop_time.setValue(time_remaining)
                    self.monoflop_time.setEnabled(False)

                    self.update_timer.start()
                else:
                    self.monoflop_pending[pin] = False

    def show_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(True)
            self.pin_button_icons[i].setVisible(True)
            self.pin_button_labels[i].setVisible(True)

        self.lines[num].setVisible(True)
    
    def hide_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(False)
            self.pin_button_icons[i].setVisible(False)
            self.pin_button_labels[i].setVisible(False)

        self.lines[num].setVisible(False)
    
    def get_current_value(self):
        value = 0
        i = 0
        for b in self.pin_buttons:
            if 'Low' in b.text():
                value |= (1 << i) 
            i += 1
        return value
    
    def set_group_pressed(self):
        group = ['n', 'n', 'n', 'n']
        for i in range(len(self.groups)):
            text = self.groups[i].currentText()
            if 'Port A' in text:
                group[i] = 'a' 
            elif 'Port B' in text:
                group[i] = 'b' 
            elif 'Port C' in text:
                group[i] = 'c' 
            elif 'Port D' in text:
                group[i] = 'd'
                 
        self.ido4.set_group(group)
        self.reconfigure_everything()
    
    def pin_button_pressed(self, button):
        value = self.get_current_value()
        if 'High' in self.pin_buttons[button].text():
            value |= (1 << button)
            self.pin_buttons[button].setText('Switch Low')
            self.pin_button_icons[button].setPixmap(self.vcc_pixmap)
        else:
            value &= ~(1 << button)
            self.pin_buttons[button].setText('Switch High')
            self.pin_button_icons[button].setPixmap(self.gnd_pixmap)
            
        self.ido4.set_value(value)

        for pin in range(16):
            self.monoflop_pending[pin] = False

        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        self.monoflop_time.setValue(self.monoflop_time_before[pin])
        self.monoflop_time.setEnabled(True)

    def cb_monoflop(self, pin_mask, value_mask):
        for pin in range(16):
            if (1 << pin) & pin_mask:
                self.monoflop_pending[pin] = False

                if (1 << pin) & value_mask:
                    self.pin_buttons[pin].setText('Switch Low')
                    self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
                else:
                    self.pin_buttons[pin].setText('Switch High')
                    self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

        if sum(self.monoflop_pending) == 0:
            self.update_timer.stop()

        current_pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if (1 << current_pin) & pin_mask:
            self.monoflop_time.setValue(self.monoflop_time_before[current_pin])
            self.monoflop_time.setEnabled(True)

    def monoflop_pin_changed(self):
        try:
            pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        except ValueError:
            return

        if self.monoflop_pending[pin]:
            value, time, time_remaining = self.ido4.get_monoflop(pin)
            self.monoflop_time.setValue(time_remaining)
            self.monoflop_time.setEnabled(False)
        else:
            self.monoflop_time.setValue(self.monoflop_time_before[pin])
            self.monoflop_time.setEnabled(True)

    def monoflop_go_pressed(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if self.monoflop_pending[pin]:
            time = self.monoflop_time_before[pin]
        else:
            time = self.monoflop_time.value()

        value = self.monoflop_state.currentIndex() == 0

        self.monoflop_time.setEnabled(False)
        self.monoflop_time_before[pin] = time
        self.monoflop_pending[pin] = True
        self.ido4.set_monoflop(1 << pin, value << pin, time)

        if value:
            self.pin_buttons[pin].setText('Switch Low')
            self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
        else:
            self.pin_buttons[pin].setText('Switch High')
            self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

        self.update_timer.start()

    def update(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if self.monoflop_pending[pin]:
            value, time, time_remaining = self.ido4.get_monoflop(pin)
            self.monoflop_time.setValue(time_remaining)
