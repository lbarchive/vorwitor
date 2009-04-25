import sys
from time import time

from PyQt4.QtCore import QObject, QTimer, SIGNAL
from PyQt4.QtGui import QLabel, QSizePolicy

from vorwitor.logger import logger


class Notification:
  
  NOTIFICATION_DURATION = 5
  NOTIFICATION_OFFSET_X = 5
  NOTIFICATION_OFFSET_Y = 5
  NOTIFICATION_GAP_Y = 5

  def __init__(self):

    self._notifications = []
    self._notification_timer = QTimer(self)
    self._notification_timer.setInterval(1000)
    QObject.connect(self._notification_timer, SIGNAL("timeout()"), self.check_notification)
    self._notification_timer.start()

  def add_notification(self, message):

    logger.debug('Adding notification')
    label = QLabel(message, self)
    if self.focus_mode:
      label.setStyleSheet('color: #ffffff; border-width: 2px; border-style: solid; border-radius: 5px; border-color: rgba(80, 80, 80, 128); background-color: rgba(200, 200, 200,128)')
    else:
      label.setStyleSheet('color: #ffffff; border-width: 2px; border-style: solid; border-radius: 5px; border-color: rgba(200, 40, 200, 128); background-color: rgba(200,40,40,128)')
    label.resize(label.sizeHint())

    # Put in place
    if self._notifications:
      last = self._notifications[-1][1]
      label.move(self.NOTIFICATION_OFFSET_X, last.y() + last.height() + self.NOTIFICATION_GAP_Y)
    else:
      label.move(self.NOTIFICATION_OFFSET_X, self.NOTIFICATION_OFFSET_Y)

    self._notifications.append((time(), label))
    
    logger.debug('Notification count: %d' % len(self._notifications))
    label.show()

  def check_notification(self):

    now = time()
    idx = 0
    last_y = self.NOTIFICATION_GAP_Y
    while self._notifications:
      noti = self._notifications[idx]
      if noti[0] + self.NOTIFICATION_DURATION < now:
        logger.debug('Destroying notification %s' % noti[1].text())
        noti[1].setParent(None)
        del self._notifications[idx]
        logger.debug('Notification count: %d' % len(self._notifications))
      else:
        # Reset position
        noti[1].move(self.NOTIFICATION_OFFSET_X, last_y)
        last_y += noti[1].height() + self.NOTIFICATION_GAP_Y
        idx += 1
      if idx >= len(self._notifications):
        break
#    else:
#      logger.debug('Notification count: %d' % len(self._notifications))
