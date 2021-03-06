# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

utils.py: General Utilites

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

from PyQt4.QtCore import QDir, QObject, pyqtSignal
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog
import os
import sys
import threading

class CallbackEmulator(QObject):
    qtcb_data = pyqtSignal(object)
    qtcb_error = pyqtSignal()

    def __init__(self, data_getter, data_callback, error_callback, use_data_signal=True):
        QObject.__init__(self)

        self.period = 0 # milliseconds
        self.timer = None
        self.data_getter = data_getter
        self.use_data_signal = use_data_signal
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.last_data = None

        if self.use_data_signal:
            self.qtcb_data.connect(self.data_callback)

        if error_callback != None:
            self.qtcb_error.connect(self.error_callback)

    def set_period(self, period):
        self.period = period

        if self.period > 0 and self.timer == None:
            self.timer = threading.Timer(self.period / 1000.0, self.update)
            self.timer.start()

    def update(self):
        self.timer = None

        if self.period < 1:
            # period was set to 0 in the meantime, ignore update
            return

        try:
            data = self.data_getter()
        except:
            self.qtcb_error.emit()

            # an error occurred, retry in 5 seconds if period was not set
            # to 0 in the meantime
            if self.period > 0:
                self.timer = threading.Timer(5, self.update)
                self.timer.start()

            return

        if self.last_data != data:
            self.last_data = data

            if self.use_data_signal:
                self.qtcb_data.emit(data)
            else:
                self.data_callback(data)

        if self.period > 0:
            self.timer = threading.Timer(self.period / 1000.0, self.update)
            self.timer.start()

def get_program_path():
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if hasattr(sys, 'frozen'):
        path = sys.executable
    else:
        path = __file__

    return os.path.dirname(os.path.realpath(unicode(path, sys.getfilesystemencoding())))

def get_resources_path():
    if sys.platform == "darwin" and hasattr(sys, 'frozen'):
        return os.path.join(os.path.split(get_program_path())[0], 'Resources')
    else:
        return get_program_path()

def get_home_path():
    return QDir.toNativeSeparators(QDir.homePath())

def get_open_file_name(*args, **kwargs):
    filename = QFileDialog.getOpenFileName(*args, **kwargs)

    if len(filename) > 0:
        filename = QDir.toNativeSeparators(filename)

    return filename

def get_open_file_names(*args, **kwargs):
    filenames = []

    for filename in QFileDialog.getOpenFileNames(*args, **kwargs):
        filenames.append(QDir.toNativeSeparators(filename))

    return filenames

def get_save_file_name(*args, **kwargs):
    filename = QFileDialog.getSaveFileName(*args, **kwargs)

    if len(filename) > 0:
        filename = QDir.toNativeSeparators(filename)

    return filename

def get_existing_directory(*args, **kwargs):
    directory = QFileDialog.getExistingDirectory(*args, **kwargs)

    if len(directory) > 0:
        directory = QDir.toNativeSeparators(directory)

        # FIXME: on Mac OS X the getExistingDirectory() might return the directory with
        #        the last part being invalid, try to find the valid part of the directory
        if sys.platform == 'darwin':
            while len(directory) > 0 and not os.path.isdir(directory):
                directory = os.path.split(directory)[0]

    return directory

def get_main_window():
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget

    return None
