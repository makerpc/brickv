# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_utils.py: Program Utils

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

from PyQt4.QtCore import Qt, QDir, QVariant, QDateTime
from PyQt4.QtGui import QListWidget, QListWidgetItem, QTreeWidgetItem, \
                        QProgressDialog, QProgressBar, QInputDialog
from brickv.plugin_system.plugins.red.api import REDProgram
import re
import posixpath
from collections import namedtuple

ExecutableVersion = namedtuple('ExecutableVersion', 'executable version')

# source: absolute path on host in host format
# target: path relative to bin directory on RED Brick in POSIX format
Upload = namedtuple('Upload', 'source target')

# source: path relative to bin directory on RED Brick in POSIX format
# target: path relative to download directory on host in host format
Download = namedtuple('Download', 'source target')


class Constants(object):
    PAGE_GENERAL    = 1001
    PAGE_FILES      = 1002
    PAGE_C          = 1003
    PAGE_CSHARP     = 1004
    PAGE_DELPHI     = 1005
    PAGE_JAVA       = 1006
    PAGE_JAVASCRIPT = 1007
    PAGE_OCTAVE     = 1008
    PAGE_PERL       = 1009
    PAGE_PHP        = 1010
    PAGE_PYTHON     = 1011
    PAGE_RUBY       = 1012
    PAGE_SHELL      = 1013
    PAGE_VBNET      = 1014
    PAGE_ARGUMENTS  = 1015
    PAGE_STDIO      = 1016
    PAGE_SCHEDULE   = 1017
    PAGE_SUMMARY    = 1018
    PAGE_UPLOAD     = 1019
    PAGE_DOWNLOAD   = 1020

    # must match item order in combo_language on general page
    LANGUAGE_INVALID    = 0
    LANGUAGE_SEPARATOR  = 1 # horizontal line in combo box
    LANGUAGE_C          = 2
    LANGUAGE_CSHARP     = 3
    LANGUAGE_DELPHI     = 4
    LANGUAGE_JAVA       = 5
    LANGUAGE_JAVASCRIPT = 6
    LANGUAGE_OCTAVE     = 7
    LANGUAGE_PERL       = 8
    LANGUAGE_PHP        = 9
    LANGUAGE_PYTHON     = 10
    LANGUAGE_RUBY       = 11
    LANGUAGE_SHELL      = 12
    LANGUAGE_VBNET      = 13

    language_display_names = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_SEPARATOR:  '<separator>',
        LANGUAGE_C:          'C/C++',
        LANGUAGE_CSHARP:     'C#',
        LANGUAGE_DELPHI:     'Delphi/Lazarus',
        LANGUAGE_JAVA:       'Java',
        LANGUAGE_JAVASCRIPT: 'JavaScript',
        LANGUAGE_OCTAVE:     'Octave',
        LANGUAGE_PERL:       'Perl',
        LANGUAGE_PHP:        'PHP',
        LANGUAGE_PYTHON:     'Python',
        LANGUAGE_RUBY:       'Ruby',
        LANGUAGE_SHELL:      'Shell',
        LANGUAGE_VBNET:      'Visual Basic .NET'
    }

    language_api_names = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_SEPARATOR:  '<separator>',
        LANGUAGE_C:          'c',
        LANGUAGE_CSHARP:     'csharp',
        LANGUAGE_DELPHI:     'delphi',
        LANGUAGE_JAVA:       'java',
        LANGUAGE_JAVASCRIPT: 'javascript',
        LANGUAGE_OCTAVE:     'octave',
        LANGUAGE_PERL:       'perl',
        LANGUAGE_PHP:        'php',
        LANGUAGE_PYTHON:     'python',
        LANGUAGE_RUBY:       'ruby',
        LANGUAGE_SHELL:      'shell',
        LANGUAGE_VBNET:      'vbnet'
    }

    language_pages = {
        LANGUAGE_C:          PAGE_C,
        LANGUAGE_CSHARP:     PAGE_CSHARP,
        LANGUAGE_DELPHI:     PAGE_DELPHI,
        LANGUAGE_JAVA:       PAGE_JAVA,
        LANGUAGE_JAVASCRIPT: PAGE_JAVASCRIPT,
        LANGUAGE_OCTAVE:     PAGE_OCTAVE,
        LANGUAGE_PERL:       PAGE_PERL,
        LANGUAGE_PHP:        PAGE_PHP,
        LANGUAGE_PYTHON:     PAGE_PYTHON,
        LANGUAGE_RUBY:       PAGE_RUBY,
        LANGUAGE_SHELL:      PAGE_SHELL,
        LANGUAGE_VBNET:      PAGE_VBNET
    }

    @staticmethod
    def get_language(language_api_name):
        return get_key_from_value(Constants.language_api_names, language_api_name)

    @staticmethod
    def get_language_display_name(language_api_name):
        return Constants.language_display_names[Constants.get_language(language_api_name)]

    @staticmethod
    def get_language_page(language_api_name):
        return Constants.language_pages[Constants.get_language(language_api_name)]

    arguments_help = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_SEPARATOR:  '<separator>',
        LANGUAGE_C:          'This list of arguments will be passed to the main() function.',
        LANGUAGE_CSHARP:     'This list of arguments will be passed to the Main() method.',
        LANGUAGE_DELPHI:     'This list of arguments will be available as ParamStr array.',
        LANGUAGE_JAVA:       'This list of arguments will be passed to the main() method.',
        LANGUAGE_JAVASCRIPT: 'This list of arguments will be available as process.argv array.',
        LANGUAGE_OCTAVE:     'This list of arguments can be accessed by calling argv().',
        LANGUAGE_PERL:       'This list of arguments will be available as @ARGV array.',
        LANGUAGE_PHP:        'This list of arguments will be available as $argv array.',
        LANGUAGE_PYTHON:     'This list of arguments will be available as sys.argv list.',
        LANGUAGE_RUBY:       'This list of arguments will be available as ARGV array.',
        LANGUAGE_SHELL:      'This list of arguments will be available as $1 to $n.',
        LANGUAGE_VBNET:      'This list of arguments can be accessed by calling Environment.GetCommandLineArgs()'
    }

    language_file_ending = { # endswith XXX sorted by file ending index
        LANGUAGE_INVALID:    [],
        LANGUAGE_SEPARATOR:  [],
        LANGUAGE_C:          [''],
        LANGUAGE_CSHARP:     ['', '.exe'],
        LANGUAGE_DELPHI:     ['', ('.pas', '.pp')],
        LANGUAGE_JAVA:       ['', '.jar'],
        LANGUAGE_JAVASCRIPT: ['', '.js'],
        LANGUAGE_OCTAVE:     ['', '.m'],
        LANGUAGE_PERL:       ['', '.pl'],
        LANGUAGE_PHP:        ['', ('.php', '.php2', '.php3', '.php4', '.php5')],
        LANGUAGE_PYTHON:     ['', '.py'],
        LANGUAGE_RUBY:       ['', '.rb'],
        LANGUAGE_SHELL:      ['', ('.sh', '.bash')],
        LANGUAGE_VBNET:      ['', '.exe'],
    }

    # must match item order in combo_start_mode on C/C++ page
    C_START_MODE_EXECUTABLE = 0

    c_start_mode_api_names = {
        C_START_MODE_EXECUTABLE: 'executable'
    }

    c_start_mode_display_names = {
        C_START_MODE_EXECUTABLE: 'Executable'
    }

    @staticmethod
    def get_c_start_mode(c_start_mode_api_name):
        try:
            return get_key_from_value(Constants.c_start_mode_api_names, c_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_C_START_MODE

    # must match item order in combo_start_mode on C# page
    CSHARP_START_MODE_EXECUTABLE = 0

    csharp_start_mode_api_names = {
        CSHARP_START_MODE_EXECUTABLE: 'executable'
    }

    csharp_start_mode_display_names = {
        CSHARP_START_MODE_EXECUTABLE: 'Executable'
    }

    @staticmethod
    def get_csharp_start_mode(csharp_start_mode_api_name):
        try:
            return get_key_from_value(Constants.csharp_start_mode_api_names, csharp_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_CSHARP_START_MODE

    # must match item order in combo_start_mode on Delphi/Lazarus page
    DELPHI_START_MODE_EXECUTABLE = 0

    delphi_start_mode_api_names = {
        DELPHI_START_MODE_EXECUTABLE: 'executable'
    }

    delphi_start_mode_display_names = {
        DELPHI_START_MODE_EXECUTABLE: 'Executable'
    }

    @staticmethod
    def get_delphi_start_mode(delphi_start_mode_api_name):
        try:
            return get_key_from_value(Constants.delphi_start_mode_api_names, delphi_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_DELPHI_START_MODE

    # must match item order in combo_start_mode on Java page
    JAVA_START_MODE_MAIN_CLASS = 0
    JAVA_START_MODE_JAR_FILE   = 1

    java_start_mode_api_names = {
        JAVA_START_MODE_MAIN_CLASS: 'main_class',
        JAVA_START_MODE_JAR_FILE:   'jar_file'
    }

    java_start_mode_display_names = {
        JAVA_START_MODE_MAIN_CLASS: 'Main Class',
        JAVA_START_MODE_JAR_FILE:   'JAR File'
    }

    @staticmethod
    def get_java_start_mode(java_start_mode_api_name):
        try:
            return get_key_from_value(Constants.java_start_mode_api_names, java_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_JAVA_START_MODE

    # must match item order in combo_flavor on JavaScript page
    JAVASCRIPT_FLAVOR_BROWSER = 0
    JAVASCRIPT_FLAVOR_NODEJS  = 1

    javascript_flavor_api_names = {
        JAVASCRIPT_FLAVOR_BROWSER: 'browser',
        JAVASCRIPT_FLAVOR_NODEJS:  'nodejs'
    }

    javascript_flavor_display_names = {
        JAVASCRIPT_FLAVOR_BROWSER: 'Browser',
        JAVASCRIPT_FLAVOR_NODEJS:  'Node.js'
    }

    @staticmethod
    def get_javascript_flavor(javascript_flavor_api_name):
        try:
            return get_key_from_value(Constants.javascript_flavor_api_names, javascript_flavor_api_name)
        except ValueError:
            return Constants.DEFAULT_JAVASCRIPT_FLAVOR

    # must match item order in combo_start_mode on JavaScript page
    JAVASCRIPT_START_MODE_SCRIPT_FILE = 0
    JAVASCRIPT_START_MODE_COMMAND     = 1

    javascript_start_mode_api_names = {
        JAVASCRIPT_START_MODE_SCRIPT_FILE: 'script_file',
        JAVASCRIPT_START_MODE_COMMAND:     'command',
    }

    javascript_start_mode_display_names = {
        JAVASCRIPT_START_MODE_SCRIPT_FILE: 'Script File',
        JAVASCRIPT_START_MODE_COMMAND:     'Command',
    }

    @staticmethod
    def get_javascript_start_mode(javascript_start_mode_api_name):
        try:
            return get_key_from_value(Constants.javascript_start_mode_api_names, javascript_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_JAVASCRIPT_START_MODE

    # must match item order in combo_start_mode on Octave page
    OCTAVE_START_MODE_SCRIPT_FILE = 0

    octave_start_mode_api_names = {
        OCTAVE_START_MODE_SCRIPT_FILE: 'script_file'
    }

    octave_start_mode_display_names = {
        OCTAVE_START_MODE_SCRIPT_FILE: 'Script File'
    }

    @staticmethod
    def get_octave_start_mode(octave_start_mode_api_name):
        try:
            return get_key_from_value(Constants.octave_start_mode_api_names, octave_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_OCTAVE_START_MODE

    # must match item order in combo_start_mode on Perl page
    PERL_START_MODE_SCRIPT_FILE = 0
    PERL_START_MODE_COMMAND     = 1

    perl_start_mode_api_names = {
        PERL_START_MODE_SCRIPT_FILE: 'script_file',
        PERL_START_MODE_COMMAND:     'command',
    }

    perl_start_mode_display_names = {
        PERL_START_MODE_SCRIPT_FILE: 'Script File',
        PERL_START_MODE_COMMAND:     'Command',
    }

    @staticmethod
    def get_perl_start_mode(perl_start_mode_api_name):
        try:
            return get_key_from_value(Constants.perl_start_mode_api_names, perl_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_PERL_START_MODE

    # must match item order in combo_start_mode on PHP page
    PHP_START_MODE_SCRIPT_FILE   = 0
    PHP_START_MODE_COMMAND       = 1
    PHP_START_MODE_WEB_INTERFACE = 2

    php_start_mode_api_names = {
        PHP_START_MODE_SCRIPT_FILE:   'script_file',
        PHP_START_MODE_COMMAND:       'command',
        PHP_START_MODE_WEB_INTERFACE: 'web_interface',
    }

    php_start_mode_display_names = {
        PHP_START_MODE_SCRIPT_FILE:   'Script File',
        PHP_START_MODE_COMMAND:       'Command',
        PHP_START_MODE_WEB_INTERFACE: 'Web Interface',
    }

    @staticmethod
    def get_php_start_mode(php_start_mode_api_name):
        try:
            return get_key_from_value(Constants.php_start_mode_api_names, php_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_PHP_START_MODE

    # must match item order in combo_start_mode on Python page
    PYTHON_START_MODE_SCRIPT_FILE   = 0
    PYTHON_START_MODE_MODULE_NAME   = 1
    PYTHON_START_MODE_COMMAND       = 2
    PYTHON_START_MODE_WEB_INTERFACE = 3

    python_start_mode_api_names = {
        PYTHON_START_MODE_SCRIPT_FILE:   'script_file',
        PYTHON_START_MODE_MODULE_NAME:   'module_name',
        PYTHON_START_MODE_COMMAND:       'command',
        PYTHON_START_MODE_WEB_INTERFACE: 'web_interface',
    }

    python_start_mode_display_names = {
        PYTHON_START_MODE_SCRIPT_FILE:   'Script File',
        PYTHON_START_MODE_MODULE_NAME:   'Module Name',
        PYTHON_START_MODE_COMMAND:       'Command',
        PYTHON_START_MODE_WEB_INTERFACE: 'Web Interface',
    }

    @staticmethod
    def get_python_start_mode(python_start_mode_api_name):
        try:
            return get_key_from_value(Constants.python_start_mode_api_names, python_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_PYTHON_START_MODE

    # must match item order in combo_start_mode on Ruby page
    RUBY_START_MODE_SCRIPT_FILE = 0
    RUBY_START_MODE_COMMAND     = 1

    ruby_start_mode_api_names = {
        RUBY_START_MODE_SCRIPT_FILE: 'script_file',
        RUBY_START_MODE_COMMAND:     'command',
    }

    ruby_start_mode_display_names = {
        RUBY_START_MODE_SCRIPT_FILE: 'Script File',
        RUBY_START_MODE_COMMAND:     'Command',
    }

    @staticmethod
    def get_ruby_start_mode(ruby_start_mode_api_name):
        try:
            return get_key_from_value(Constants.ruby_start_mode_api_names, ruby_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_RUBY_START_MODE

    # must match item order in combo_start_mode on Shell page
    SHELL_START_MODE_SCRIPT_FILE = 0
    SHELL_START_MODE_COMMAND     = 1

    shell_start_mode_api_names = {
        SHELL_START_MODE_SCRIPT_FILE: 'script_file',
        SHELL_START_MODE_COMMAND:     'command',
    }

    shell_start_mode_display_names = {
        SHELL_START_MODE_SCRIPT_FILE: 'Script File',
        SHELL_START_MODE_COMMAND:     'Command',
    }

    @staticmethod
    def get_shell_start_mode(shell_start_mode_api_name):
        try:
            return get_key_from_value(Constants.shell_start_mode_api_names, shell_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_SHELL_START_MODE

    # must match item order in combo_start_mode on VB.NET page
    VBNET_START_MODE_EXECUTABLE = 0

    vbnet_start_mode_api_names = {
        VBNET_START_MODE_EXECUTABLE: 'executable'
    }

    vbnet_start_mode_display_names = {
        VBNET_START_MODE_EXECUTABLE: 'Executable'
    }

    @staticmethod
    def get_vbnet_start_mode(vbnet_start_mode_api_name):
        try:
            return get_key_from_value(Constants.vbnet_start_mode_api_names, vbnet_start_mode_api_name)
        except ValueError:
            return Constants.DEFAULT_VBNET_START_MODE

    # must match item order in combo_stdin_redirection on stdio page
    STDIN_REDIRECTION_DEV_NULL = 0
    STDIN_REDIRECTION_PIPE     = 1
    STDIN_REDIRECTION_FILE     = 2

    api_stdin_redirections = {
        STDIN_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDIN_REDIRECTION_PIPE:     REDProgram.STDIO_REDIRECTION_PIPE,
        STDIN_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE
    }

    api_stdin_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL: '/dev/null',
        REDProgram.STDIO_REDIRECTION_PIPE:     'Pipe',
        REDProgram.STDIO_REDIRECTION_FILE:     'File'
    }

    @staticmethod
    def get_stdin_redirection(api_stdin_redirection):
        return get_key_from_value(Constants.api_stdin_redirections, api_stdin_redirection)

    @staticmethod
    def get_stdin_redirection_display_name(stdin_redirection):
        return Constants.api_stdin_redirection_display_names[Constants.api_stdin_redirections[stdin_redirection]]

    # must match item order in combo_stdout_redirection on stdio page
    STDOUT_REDIRECTION_DEV_NULL       = 0
    STDOUT_REDIRECTION_FILE           = 1
    STDOUT_REDIRECTION_INDIVIDUAL_LOG = 2
    STDOUT_REDIRECTION_CONTINUOUS_LOG = 3

    api_stdout_redirections = {
        STDOUT_REDIRECTION_DEV_NULL:       REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDOUT_REDIRECTION_FILE:           REDProgram.STDIO_REDIRECTION_FILE,
        STDOUT_REDIRECTION_INDIVIDUAL_LOG: REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG,
        STDOUT_REDIRECTION_CONTINUOUS_LOG: REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG,
    }

    api_stdout_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL:       '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:           'File',
        REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG: 'Individual Log Files',
        REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG: 'Continuous Log File'
    }

    @staticmethod
    def get_stdout_redirection(api_stdout_redirection):
        return get_key_from_value(Constants.api_stdout_redirections, api_stdout_redirection)

    @staticmethod
    def get_stdout_redirection_display_name(stdout_redirection):
        return Constants.api_stdout_redirection_display_names[Constants.api_stdout_redirections[stdout_redirection]]

    # must match item order in combo_stderr_redirection on stdio page
    STDERR_REDIRECTION_DEV_NULL       = 0
    STDERR_REDIRECTION_FILE           = 1
    STDERR_REDIRECTION_INDIVIDUAL_LOG = 2
    STDERR_REDIRECTION_CONTINUOUS_LOG = 3
    STDERR_REDIRECTION_STDOUT         = 4

    api_stderr_redirections = {
        STDERR_REDIRECTION_DEV_NULL:       REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDERR_REDIRECTION_FILE:           REDProgram.STDIO_REDIRECTION_FILE,
        STDERR_REDIRECTION_INDIVIDUAL_LOG: REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG,
        STDERR_REDIRECTION_CONTINUOUS_LOG: REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG,
        STDERR_REDIRECTION_STDOUT:         REDProgram.STDIO_REDIRECTION_STDOUT
    }

    api_stderr_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL:       '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:           'File',
        REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG: 'Individual Log Files',
        REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG: 'Continuous Log File',
        REDProgram.STDIO_REDIRECTION_STDOUT:         'Standard Output'
    }

    @staticmethod
    def get_stderr_redirection(api_stderr_redirection):
        return get_key_from_value(Constants.api_stderr_redirections, api_stderr_redirection)

    @staticmethod
    def get_stderr_redirection_display_name(stderr_redirection):
        return Constants.api_stderr_redirection_display_names[Constants.api_stderr_redirections[stderr_redirection]]

    # must match item order in combo_start_mode on schedule page
    START_MODE_NEVER     = 0
    START_MODE_ALWAYS    = 1
    START_MODE_INTERVAL  = 2
    START_MODE_CRON      = 3
    START_MODE_SEPARATOR = 4 # horizontal line in combo box
    START_MODE_ONCE      = 5 # never + start from upload page

    api_start_modes = {
        START_MODE_NEVER:    REDProgram.START_MODE_NEVER,
        START_MODE_ALWAYS:   REDProgram.START_MODE_ALWAYS,
        START_MODE_INTERVAL: REDProgram.START_MODE_INTERVAL,
        START_MODE_CRON:     REDProgram.START_MODE_CRON
    }

    api_start_mode_display_names = {
        REDProgram.START_MODE_NEVER:    'Never',
        REDProgram.START_MODE_ALWAYS:   'Always',
        REDProgram.START_MODE_INTERVAL: 'Interval',
        REDProgram.START_MODE_CRON:     'Cron'
    }

    @staticmethod
    def get_start_mode(api_start_mode):
        return get_key_from_value(Constants.api_start_modes, api_start_mode)

    @staticmethod
    def get_start_mode_display_name(start_mode):
        return Constants.api_start_mode_display_names[Constants.api_start_modes[start_mode]]

    api_scheduler_state_display_name = {
        REDProgram.SCHEDULER_STATE_STOPPED: 'Stopped',
        REDProgram.SCHEDULER_STATE_RUNNING: 'Running'
    }

    DEFAULT_C_START_MODE          = C_START_MODE_EXECUTABLE
    DEFAULT_CSHARP_START_MODE     = CSHARP_START_MODE_EXECUTABLE
    DEFAULT_DELPHI_START_MODE     = DELPHI_START_MODE_EXECUTABLE
    DEFAULT_JAVA_START_MODE       = JAVA_START_MODE_MAIN_CLASS
    DEFAULT_JAVASCRIPT_FLAVOR     = JAVASCRIPT_FLAVOR_BROWSER
    DEFAULT_JAVASCRIPT_START_MODE = JAVASCRIPT_START_MODE_SCRIPT_FILE
    DEFAULT_OCTAVE_START_MODE     = OCTAVE_START_MODE_SCRIPT_FILE
    DEFAULT_PERL_START_MODE       = PERL_START_MODE_SCRIPT_FILE
    DEFAULT_PHP_START_MODE        = PHP_START_MODE_SCRIPT_FILE
    DEFAULT_PYTHON_START_MODE     = PYTHON_START_MODE_SCRIPT_FILE
    DEFAULT_RUBY_START_MODE       = RUBY_START_MODE_SCRIPT_FILE
    DEFAULT_SHELL_START_MODE      = SHELL_START_MODE_SCRIPT_FILE
    DEFAULT_VBNET_START_MODE      = VBNET_START_MODE_EXECUTABLE
    DEFAULT_STDIN_REDIRECTION     = STDIN_REDIRECTION_PIPE
    DEFAULT_STDOUT_REDIRECTION    = STDOUT_REDIRECTION_CONTINUOUS_LOG
    DEFAULT_STDERR_REDIRECTION    = STDERR_REDIRECTION_STDOUT
    DEFAULT_START_MODE            = START_MODE_ALWAYS


# workaround miscalculated initial size-hint for initially hidden QListWidgets
class ExpandingListWidget(QListWidget):
    # overrides QListWidget.sizeHint
    def sizeHint(self):
        size = QListWidget.sizeHint(self)

        if size.height() < 2000:
            size.setHeight(2000)

        return size


class ExpandingProgressDialog(QProgressDialog):
    def hide_progress_text(self):
        progress = QProgressBar(self)
        progress.setTextVisible(False)
        self.setBar(progress)

    # overrides QProgressDialog.sizeHint
    def sizeHint(self):
        size = QProgressDialog.sizeHint(self)

        if size.width() < 400:
            size.setWidth(400)

        return size


class ExpandingInputDialog(QInputDialog):
    # overrides QInputDialog.sizeHint
    def sizeHint(self):
        size = QInputDialog.sizeHint(self)

        if size.width() < 400:
            size.setWidth(400)

        return size


class ListWidgetEditor(object):
    def __init__(self, label_items, list_items, label_items_help,
                 button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_text):
        self.label_items        = label_items
        self.list_items         = list_items
        self.label_items_help   = label_items_help
        self.button_add_item    = button_add_item
        self.button_remove_item = button_remove_item
        self.button_up_item     = button_up_item
        self.button_down_item   = button_down_item
        self.new_item_text      = new_item_text
        self.new_item_counter   = 1

        self.list_items.itemSelectionChanged.connect(self.update_ui_state)

        if self.button_add_item != None:
            self.button_add_item.clicked.connect(self.add_new_item)

        self.button_remove_item.clicked.connect(self.remove_selected_item)
        self.button_up_item.clicked.connect(self.up_selected_item)
        self.button_down_item.clicked.connect(self.down_selected_item)

        self.original_items = []

        for row in range(self.list_items.count()):
            self.original_items.append(self.list_items.item(row).text())

    def update_ui_state(self):
        has_selection = len(self.list_items.selectedItems()) > 0
        item_count = self.list_items.count()

        if has_selection:
            selected_index = self.list_items.row(self.list_items.selectedItems()[0])
        else:
            selected_index = -1

        self.button_remove_item.setEnabled(has_selection)
        self.button_up_item.setEnabled(item_count > 1 and has_selection and selected_index > 0)
        self.button_down_item.setEnabled(item_count > 1 and has_selection and selected_index < item_count - 1)

    def set_visible(self, visible):
        self.label_items.setVisible(visible)
        self.list_items.setVisible(visible)
        self.label_items_help.setVisible(visible)

        if self.button_add_item != None:
            self.button_add_item.setVisible(visible)

        self.button_remove_item.setVisible(visible)
        self.button_up_item.setVisible(visible)
        self.button_down_item.setVisible(visible)

    def add_item(self, text, edit_item=False, select_item=False):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.list_items.addItem(item)

        if edit_item:
            self.list_items.setCurrentItem(item)
            self.list_items.setFocus()
            self.list_items.editItem(item)
        elif select_item:
            self.list_items.setCurrentItem(item)
            self.list_items.setFocus()

        self.update_ui_state()

    def add_new_item(self):
        counter = self.new_item_counter
        self.new_item_counter += 1

        self.add_item(self.new_item_text.format(counter), edit_item=True)
        self.list_items.verticalScrollBar().setValue(self.list_items.verticalScrollBar().maximum())

    def remove_selected_item(self):
        for item in self.list_items.selectedItems():
            self.list_items.takeItem(self.list_items.row(item))

        self.update_ui_state()

    def up_selected_item(self):
        selected_items = self.list_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.list_items.row(selected_items[0])
        item = self.list_items.takeItem(row)

        self.list_items.insertItem(row - 1, item)
        self.list_items.setCurrentRow(row - 1)

    def down_selected_item(self):
        selected_items = self.list_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.list_items.row(selected_items[0])
        item = self.list_items.takeItem(row)

        self.list_items.insertItem(row + 1, item)
        self.list_items.setCurrentRow(row + 1)

    def clear(self):
        self.new_item_counter = 1

        self.list_items.clear()

    def reset(self):
        self.clear()

        for original_item in self.original_items:
            self.add_item(original_item)

    def get_items(self):
        items = []

        for row in range(self.list_items.count()):
            items.append(self.list_items.item(row).text())

        return items


class TreeWidgetEditor(object):
    def __init__(self, label_items, tree_items, label_items_help,
                 button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_texts):
        self.label_items        = label_items
        self.tree_items         = tree_items
        self.label_items_help   = label_items_help
        self.button_add_item    = button_add_item
        self.button_remove_item = button_remove_item
        self.button_up_item     = button_up_item
        self.button_down_item   = button_down_item
        self.new_item_texts     = new_item_texts
        self.new_item_counter   = 1

        self.tree_items.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_item.clicked.connect(self.add_new_item)
        self.button_remove_item.clicked.connect(self.remove_selected_item)
        self.button_up_item.clicked.connect(self.up_selected_item)
        self.button_down_item.clicked.connect(self.down_selected_item)

        self.original_items = []

        root = self.tree_items.invisibleRootItem()

        for row in range(root.childCount()):
            child = root.child(row)
            item = []

            for column in range(child.columnCount()):
                item.append(child.text(column))

            self.original_items.append(item)

    def update_ui_state(self):
        has_selection = len(self.tree_items.selectedItems()) > 0
        item_count = self.tree_items.invisibleRootItem().childCount()

        if has_selection:
            selected_index = self.tree_items.indexOfTopLevelItem(self.tree_items.selectedItems()[0])
        else:
            selected_index = -1

        self.button_remove_item.setEnabled(has_selection)
        self.button_up_item.setEnabled(item_count > 1 and has_selection and selected_index > 0)
        self.button_down_item.setEnabled(item_count > 1 and has_selection and selected_index < item_count - 1)

    def set_visible(self, visible):
        self.label_items.setVisible(visible)
        self.tree_items.setVisible(visible)
        self.label_items_help.setVisible(visible)
        self.button_add_item.setVisible(visible)
        self.button_remove_item.setVisible(visible)
        self.button_up_item.setVisible(visible)
        self.button_down_item.setVisible(visible)

    def add_item(self, texts, edit_item=False, select_item=False):
        item = QTreeWidgetItem(texts)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.tree_items.addTopLevelItem(item)

        if edit_item:
            self.tree_items.setCurrentItem(item)
            self.tree_items.setFocus()
            self.tree_items.editItem(item)
        elif select_item:
            self.tree_items.setCurrentItem(item)
            self.tree_items.setFocus()

        self.update_ui_state()

    def add_new_item(self):
        texts = []

        for text in self.new_item_texts:
            texts.append(text.format(self.new_item_counter))

        self.new_item_counter += 1

        self.add_item(texts, edit_item=True)
        self.tree_items.verticalScrollBar().setValue(self.tree_items.verticalScrollBar().maximum())

    def remove_selected_item(self):
        for item in self.tree_items.selectedItems():
            row = self.tree_items.indexOfTopLevelItem(item)
            self.tree_items.takeTopLevelItem(row)

        self.update_ui_state()

    def up_selected_item(self):
        selected_items = self.tree_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.tree_items.indexOfTopLevelItem(selected_items[0])
        item = self.tree_items.takeTopLevelItem(row)

        self.tree_items.insertTopLevelItem(row - 1, item)
        self.tree_items.setCurrentItem(item)

    def down_selected_item(self):
        selected_items = self.tree_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.tree_items.indexOfTopLevelItem(selected_items[0])
        item = self.tree_items.takeTopLevelItem(row)

        self.tree_items.insertTopLevelItem(row + 1, item)
        self.tree_items.setCurrentItem(item)

    def clear(self):
        self.new_item_counter = 1

        self.tree_items.invisibleRootItem().takeChildren()

    def reset(self):
        self.clear()

        for original_item in self.original_items:
            self.add_item(original_item)

    def get_items(self):
        items = []

        for row in range(self.tree_items.topLevelItemCount()):
            child = self.tree_items.topLevelItem(row)
            item = []

            for column in range(child.columnCount()):
                item.append(child.text(column))

            items.append(item)

        return items


class MandatoryLineEditChecker(object):
    def __init__(self, page, label, edit, regexp=None):
        self.page     = page
        self.label    = label
        self.edit     = edit
        self.regexp   = None
        self.complete = False

        if regexp != None:
            self.regexp = re.compile(regexp)

        self.edit.textChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_complete = self.complete
        text = self.edit.text()
        self.complete = len(text) > 0

        if self.complete and self.regexp != None:
            self.complete = self.regexp.match(text) != None

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


class MandatoryEditableComboBoxChecker(object):
    def __init__(self, page, label, combo):
        self.page     = page
        self.label    = label
        self.combo    = combo
        self.complete = False

        self.combo.currentIndexChanged.connect(lambda: self.check(True))
        self.combo.editTextChanged.connect(lambda: self.check(True))

        self.check(False)

    def set_current_text(self, text):
        if len(text) == 0:
            self.combo.clearEditText()
            return

        i = self.combo.findText(text)

        if i < 0:
            self.combo.addItem(text)
            i = self.combo.count() - 1

        self.combo.setCurrentIndex(i)

    def check(self, emit):
        was_complete = self.complete
        self.complete = len(self.combo.currentText()) > 0

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


# expects the combo box to be editable
# FIXME: ensure that file is relative, non-empty and does not start with ..
class MandatoryTypedFileSelector(object):
    def __init__(self, page, label_file, combo_file, label_type, combo_type, label_help):
        self.page       = page
        self.label_file = label_file
        self.combo_file = combo_file
        self.label_type = label_type
        self.combo_type = combo_type
        self.label_help = label_help

        # FIXME
        self.c1 = MandatoryEditableComboBoxChecker(page, label_file, combo_file)
        self.c2 = ComboBoxFileEndingChecker(page, combo_file, combo_type)

    def set_visible(self, visible):
        self.label_file.setVisible(visible)
        self.combo_file.setVisible(visible)
        self.label_type.setVisible(visible)
        self.combo_type.setVisible(visible)
        self.label_help.setVisible(visible)

    def set_current_text(self, text):
        # FIXME: select current combo_type based on text

        if len(text) == 0:
            self.combo_file.clearEditText()
            return

        i = self.combo_file.findText(text)

        if i < 0:
            self.combo_file.addItem(text)
            i = self.combo_file.count() - 1

        self.combo_file.setCurrentIndex(i)

    def reset(self):
        self.c2.check(False)
        self.combo_type.setCurrentIndex(1) # FIXME

    @property
    def complete(self):
        return self.c1.complete


# expects the combo box to be editable
class MandatoryDirectorySelector(object):
    def __init__(self, page, label, combo):
        self.page  = page
        self.label = label
        self.combo = combo
        self.complete = False
        self.original_items = []

        for i in range(combo.count()):
            self.original_items.append(combo.itemText(i))

        self.combo.currentIndexChanged.connect(lambda: self.check(True))
        self.combo.editTextChanged.connect(lambda: self.check(True))

    def set_visible(self, visible):
        self.combo.setVisible(visible)
        self.label.setVisible(visible)

    def set_current_text(self, text):
        if len(text) == 0:
            self.combo.clearEditText()
            return

        i = self.combo.findText(text)

        if i < 0:
            self.combo.addItem(text)
            i = self.combo.count() - 1

        self.combo.setCurrentIndex(i)

    def reset(self):
        self.combo.clear()
        self.combo.addItems(self.original_items)
        self.combo.addItems(self.page.wizard().available_directories)

        if self.combo.count() > 1 and len(self.original_items) > 0 and self.original_items[0] != '.':
            self.combo.clearEditText()

    # ensure that directory is relative, non-empty and does not start with ..
    def check(self, emit):
        was_complete  = self.complete
        directory     = QDir.cleanPath(posixpath.join(self.combo.currentText(), '.'))
        self.complete = len(directory) > 0 and \
                        not directory.startswith('/') and \
                        directory != './..' and \
                        not directory.startswith('./../') and \
                        directory != '..' and \
                        not directory.startswith('../')

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


class ComboBoxFileEndingChecker(object):
    class NoEndingCheckRequired(object):
        class NoIndexChangeRequired(object):
            def connect(self, *args, **kwargs):
                return
        currentIndexChanged = NoIndexChangeRequired()
        def currentIndex(self):
            return 0 # = *

    def __init__(self, page, combo_file, combo_ending = None):
        self.page       = page
        self.combo_file = combo_file
        if combo_ending == None:
            self.combo_ending = self.NoEndingCheckRequired()
        else:
            self.combo_ending = combo_ending

        self.combo_ending.currentIndexChanged.connect(lambda: self.check(True))

    def check(self, emit):
        self.combo_file.clear()
        self.combo_file.clearEditText()

        ends = Constants.language_file_ending[self.page.language][self.combo_ending.currentIndex()]

        for filename in sorted(self.page.wizard().available_files):
            if type(ends) != tuple:
                ends = (ends,)
            for end in ends:
                if filename.lower().endswith(end):
                    self.combo_file.addItem(filename)

        if self.combo_file.count() > 1:
            self.combo_file.clearEditText()


def get_key_from_value(dictionary, value):
    return dictionary.keys()[dictionary.values().index(value)]


def set_current_combo_index_from_data(combo, data):
    i = combo.findData(QVariant(data))

    if i >= 0:
        combo.setCurrentIndex(i)
    else:
        combo.addItem('<unknown>', QVariant(data))
        combo.setCurrentIndex(combo.count() - 1)


def timestamp_to_date_at_time(timestamp, glue=' at '):
    date = QDateTime.fromTime_t(timestamp).toString('yyyy-MM-dd')
    time = QDateTime.fromTime_t(timestamp).toString('HH:mm:ss')

    return date + glue + time


# FIXME: the values should be rouned up
def get_file_display_size(size):
    if size < 1024:
        return '%d Bytes' % size
    elif size < 1048576:
        return '%.1f kiB' % (size / 1024.0)
    else:
        return '%.1f MiB' % (size / 1048576.0)
