# Copyright (C) 2009  Yu-Jie Lin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from os import path
import re

from PyQt4 import QtGui, uic, Qt
from PyQt4.QtCore import pyqtSignature, QObject, SIGNAL
from PyQt4.QtGui import QColor, QFileDialog, QFont, QFontDialog, QFontMetrics, QMenu, QTextCharFormat, QTextCursor

from vorwitor import file as v_file
from vorwitor import spell
from vorwitor.config import config, configure_color, configure_font
from vorwitor.logger import logger
from vorwitor.ui.notification import Notification

Ui_MainWindow = uic.loadUiType(path.dirname(__file__) + '/mainwindow.ui')[0]


class MainWindow(Ui_MainWindow, QtGui.QMainWindow, Notification):

  def __init__(self):
    logger.debug('Initializing MainWindow')
    # UI initialization
    QtGui.QMainWindow.__init__(self)
    Ui_MainWindow.__init__(self)
    Notification.__init__(self)
    self.setupUi(self)

    self.file_dialog = QFileDialog(self, 'Open file...', path.expanduser('~'), 'Text (*.txt)')
    self.text_filename = ''

    self.focus_mode = False
    QtGui.QShortcut(QtGui.QKeySequence.New, self, self.new_text)
    QtGui.QShortcut(QtGui.QKeySequence.Open, self, self.open_text)
    QtGui.QShortcut(QtGui.QKeySequence.Save, self, self.save_text)
    QtGui.QShortcut(QtGui.QKeySequence("F4"), self, self.show_stats)
    QtGui.QShortcut(QtGui.QKeySequence("F11"), self, self.toogle_mode)
    QtGui.QShortcut(QtGui.QKeySequence("Ctrl+T"), self, self._test)
    logger.debug('Initialized MainWindow')
    
  def _test(self):

    self.add_notification('ABC')

  def configure_normal_mode(self):
    
    logger.debug('Configuring normal mode')
    
    width = config.getint('ui_mainwindow', 'text_width')
    spacer_width = (self.splitter.width() - width - self.splitter.handleWidth() * 2) / 2
    if spacer_width < 0:
      spacer_width = 0
#       adj_width = abs(spacer_width) * 2
#       self.resize(self.width() + adj_width, self.height())

    self.splitter.setSizes((spacer_width, width, spacer_width))

    self.set_stylesheet()

    font = QFont()
    font.fromString(config.get('ui_mainwindow', 'text_font'))
#    self.text.setFont(font)
    self.set_text_font(font)

    self.set_text_stylesheet()

    logger.debug('Configured normal mode')

  def configure_focus_mode(self):
    logger.debug('Configuring focus mode')

    width = config.getint('ui_mainwindow', 'text_width')
    spacer_width = (self.splitter.width() - width - self.splitter.handleWidth() * 2) / 2
    self.splitter.setSizes((spacer_width, width, spacer_width))
    
    self.set_focus_stylesheet()

    font = QFont()
    font.fromString(config.get('ui_mainwindow', 'text_focus_font'))
#    self.text.setFont(font)
    self.set_text_font(font)

    self.set_text_focus_stylesheet()

    logger.debug('Configured focus mode')

  def set_text_stylesheet(self, *kw):
    
    self.text.setStyleSheet('color: %s; background-color: %s' % (
        QColor(config.get('ui_mainwindow', 'text_color')).name(),
        QColor(config.get('ui_mainwindow', 'text_background_color')).name()))

  def set_text_focus_stylesheet(self, *kw):
    
    self.text.setStyleSheet('color: %s; background-color: %s' % (
        QColor(config.get('ui_mainwindow', 'text_focus_color')).name(),
        QColor(config.get('ui_mainwindow', 'text_focus_background_color')).name()))

  def set_text_font(self, font):
    
    self.text.setFont(font)

    char_fmt = QTextCharFormat()
    char_fmt.setFont(font) 

    original_cursor = self.text.textCursor()

    # Force recheck spelling
    self.text.previous_length = 0

    self.text.selectAll()
    cursor = self.text.textCursor()
    cursor.setCharFormat(char_fmt)

    self.text.setTextCursor(original_cursor)

  def set_stylesheet(self, *kw):
    
    self.setStyleSheet('QMainWindow{background-color: %s}' % (
        QColor(config.get('ui_mainwindow', 'background_color')).name()))
  
  def set_focus_stylesheet(self, *kw):
    
    #self.setStyleSheet('background-color: %s' % (
    self.setStyleSheet('QMainWindow{background-color: %s}' % (
        QColor(config.get('ui_mainwindow', 'focus_background_color')).name()))

  def _correct_word(self, action):

    spell.hook_correct_word(self, action.text())

  # Qt binding
  @pyqtSignature('QPoint')
  def on_text_customContextMenuRequested(self, pos):

    # TODO QMenu * createStandardContextMenu ()
    menu = QMenu(self)

    suggestions = spell.hook_get_suggestion(self.text)
    if suggestions:
      c_menu = menu.addMenu('Suggestions')
      for word in suggestions:
        c_menu.addAction(word)

    c_menu = menu.addMenu('Config')
    if self.focus_mode:
      c_menu.addAction('Font', lambda: configure_font(self, 'ui_mainwindow', 'text_focus_font', self.set_text_font))
      c_menu.addAction('Color', lambda: configure_color(self, 'ui_mainwindow', 'text_focus_color', self.set_text_focus_stylesheet))
      c_menu.addAction('Background color', lambda: configure_color(self, 'ui_mainwindow', 'text_focus_background_color', self.set_text_focus_stylesheet))
    else:
      c_menu.addAction('Font', lambda: configure_font(self, 'ui_mainwindow', 'text_font', self.set_text_font))
      c_menu.addAction('Color', lambda: configure_color(self, 'ui_mainwindow', 'text_color', self.set_text_stylesheet))
      c_menu.addAction('Background color', lambda: configure_color(self, 'ui_mainwindow', 'text_background_color', self.set_text_stylesheet))

    action = menu.exec_(self.text.mapToGlobal(pos))
    if action:
      parentWidget = action.parentWidget()
      if parentWidget and parentWidget.title() == 'Suggestions':
        spell.hook_correct_word(self.text, action.text())

  def pop_mainwindowContextMenu(self, pos):
    menu = QMenu(self)
    c_menu = menu.addMenu('Config')
    if self.focus_mode:
      c_menu.addAction('Background color', lambda: configure_color('ui_mainwindow', 'focus_background_color', self.set_focus_stylesheet))
    else:
      c_menu.addAction('Background color', lambda: configure_color('ui_mainwindow', 'background_color', self.focus_stylesheet))
    menu.exec_(pos)

  @pyqtSignature('QPoint')
  def on_space1_customContextMenuRequested(self, pos):

    self.pop_mainwindowContextMenu(self.space1.mapToGlobal(pos))

  @pyqtSignature('QPoint')
  def on_space2_customContextMenuRequested(self, pos):

    self.pop_mainwindowContextMenu(self.space2.mapToGlobal(pos))

  @pyqtSignature('QPoint')
  def on_mainwindow_customContextMenuRequested(self, pos):

    self.pop_mainwindowContextMenu(self.mapToGlobal(pos))

  @pyqtSignature('int, int')
  def on_splitter_splitterMoved(self, pos, index):

    config.set('ui_mainwindow', 'text_width', self.splitter.sizes()[1])

  def new_text(self):

    self.text.setPlainText('')
    self.text_filename = ''
    self.setWindowTitle('Vorwitor: New file')

  def open_text(self):

    self.file_dialog.setWindowTitle('Open file...')
    if self.file_dialog.exec_():
      filename = self.file_dialog.selectedFiles()[0]
      logger.debug('Opening file %s' % filename)
      self.text.setPlainText(v_file.open_text(filename))
      self.text_filename = filename
      self.setWindowTitle('Vorwitor: %s' % filename)
    
  def save_text(self):

    if self.text_filename:
      v_file.save_text(self.text_filename, self.text.toPlainText())
      self.add_notification('File saved')
    else:
      self.file_dialog.setWindowTitle('Save file...')
      if self.file_dialog.exec_():
        filename = self.file_dialog.selectedFiles()[0]
        logger.debug('Saving file to %s' % filename)
        v_file.save_text(filename, self.text.toPlainText())
        self.text_filename = filename
        self.setWindowTitle('Vorwitor: %s' % filename)
        self.add_notification('File saved')

  def show_stats(self):
   
    text = unicode(self.text.toPlainText())
    words = re.split('[^a-zA-Z0-9-]+|-{2,}', text)
    if words == ['']:
      words = []
    characters = re.sub('\s', '', text)
    self.add_notification('%d words, %d characters' % (len(words), len(characters)))

  @pyqtSignature('')
  def on_text_textChanged(self):

    spell.hook_textChanged(self.text)

  def toogle_mode(self):

    if not self.focus_mode:
      self.showFullScreen()
      self.configure_focus_mode()
    else:
      self.showFullScreen()
      self.showNormal()
      self.configure_normal_mode()
    self.focus_mode = not (self.focus_mode)
