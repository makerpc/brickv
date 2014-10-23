# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_java.py: New Program Wizard Java Page

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

from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.new_program_utils import *
from brickv.plugin_system.plugins.red.ui_new_program_java import Ui_NewProgramJava

class NewProgramJava(QWizardPage, Ui_NewProgramJava):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 3 of {0}: Java Configuration'.format(Constants.STEP_COUNT))

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.edit_main_class)
        self.registerField('java.jar_file', self.combo_jar_file, 'currentText')
        self.registerField('java.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.edit_main_class_checker = MandatoryLineEditChecker(self, self.edit_main_class, self.label_main_class)
        self.combo_jar_file_checker = MandatoryEditableComboBoxChecker(self, self.combo_jar_file, self.label_jar_file)
        self.combo_working_directory_checker = MandatoryEditableComboBoxChecker(self, self.combo_working_directory, self.label_working_directory)

        # FIXME: allow adding class path entries using a combo box prefilled with avialable .jar files
        self.class_path_list_editor = ListWidgetEditor(self.list_class_path,
                                                       self.button_add_class_path_entry,
                                                       self.button_remove_class_path_entry,
                                                       self.button_up_class_path_entry,
                                                       self.button_down_class_path_entry,
                                                       '<new class path entry {0}>')

        self.option_list_editor = ListWidgetEditor(self.list_options,
                                                   self.button_add_option,
                                                   self.button_remove_option,
                                                   self.button_up_option,
                                                   self.button_down_option,
                                                   '<new JVM option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify how the new Java program [{0}] should be executed.'
                         .format(unicode(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVA_START_MODE)
        self.combo_jar_file.clear()

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            if upload.target.lower().endswith('.jar'):
                self.combo_jar_file.addItem(upload.target)

        if self.combo_jar_file.count() > 1:
            self.combo_jar_file.clearEditText()

        self.check_show_advanced_options.setCheckState(Qt.Unchecked)

        directorys = self.wizard().page(Constants.PAGE_FILES).get_directorys()

        self.combo_working_directory.clear()
        self.combo_working_directory.addItem('.')
        self.combo_working_directory.addItems(directorys)

        self.class_path_list_editor.reset_items()
        self.option_list_editor.reset_items()
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_ARGUMENTS

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.field('java.start_mode').toInt()[0]

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS and \
           not self.edit_main_class_checker.valid:
            return False

        if start_mode == Constants.JAVA_START_MODE_JAR_FILE and \
           not self.combo_jar_file_checker.valid:
            return False

        return self.combo_working_directory_checker.valid and QWizardPage.isComplete(self)

    def update_ui_state(self):
        start_mode = self.field('java.start_mode').toInt()[0]
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file = start_mode == Constants.JAVA_START_MODE_JAR_FILE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_main_class.setVisible(start_mode_main_class)
        self.edit_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.label_jar_file.setVisible(start_mode_jar_file)
        self.combo_jar_file.setVisible(start_mode_jar_file)
        self.label_jar_file_help.setVisible(start_mode_jar_file)
        self.label_working_directory.setVisible(show_advanced_options)
        self.combo_working_directory.setVisible(show_advanced_options)
        self.label_options.setVisible(show_advanced_options)
        self.list_options.setVisible(show_advanced_options)
        self.label_options_help.setVisible(show_advanced_options)
        self.button_add_option.setVisible(show_advanced_options)
        self.button_remove_option.setVisible(show_advanced_options)
        self.button_up_option.setVisible(show_advanced_options)
        self.button_down_option.setVisible(show_advanced_options)

        self.class_path_list_editor.update_ui_state()
        self.option_list_editor.update_ui_state()

    def get_command(self):
        executable = '/usr/bin/java'
        arguments = self.option_list_editor.get_items()
        class_path_entries = self.class_path_list_editor.get_items()

        if len(class_path_entries) > 0:
            arguments += ['-cp', ':'.join(class_path_entries)]

        start_mode = self.field('java.start_mode').toInt()[0]

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS:
            arguments.append(unicode(self.edit_main_class.text()))
        elif start_mode == Constants.JAVA_START_MODE_JAR_FILE:
            arguments.append('-jar')
            arguments.append(unicode(self.combo_jar_file.currentText()))

        working_directory = unicode(self.field('java.working_directory').toString())

        return executable, arguments, working_directory