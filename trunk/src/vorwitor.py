#!/usr/bin/python
#
# vorwiter
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


from optparse import OptionParser
import logging
import sys

from PyQt4 import QtCore, QtGui

from vorwitor.logger import logger
from vorwitor.ui.mainwindow import MainWindow
import vorwitor


# Handling command-line arugments
parser = OptionParser()
parser.add_option('-d', '--debug',
    action='store_true', dest='debug', default=True,
    help='Output debug message')
(options, args) = parser.parse_args()


# Initializ Vorwitor
logger.info('Vorwitor initalizing')
vorwitor.initialize()

logger.info('Vorwitor starting')

app = QtGui.QApplication(sys.argv)

mainwindow = MainWindow()
mainwindow.show()
mainwindow.configure_normal_mode()

ret = app.exec_()

logger.info('Vorwitor exiting')

sys.exit(ret)
