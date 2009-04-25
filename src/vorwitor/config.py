from ConfigParser import NoSectionError, NoOptionError, RawConfigParser

from PyQt4.QtCore import pyqtSignature, QObject, QTimer, SIGNAL
from PyQt4.QtGui import QColor, QColorDialog, QFont, QFontDialog

from vorwitor import CONFIG_DIR
from vorwitor.logger import logger


def configure_color(parent, section, option, callback):

  logger.debug('Configuring color for %s.%s' % (section, option))
  color = QColorDialog.getColor(QColor(config.get(section, option)), parent)
  if color.isValid():
    logger.debug('Color configured for %s.%s: %s' % (section, option, color.name()))
    if not config.has_section(section):
      config.add_section(section)
    config.set(section, option, color.name())
    callback(color)
  else:
    logger.debug('Color configuration canceled')
  return color

def configure_font(parent, section, option, callback):

  logger.debug('Configuring font for %s.%s' % (section, option))
  i_font = QFont()
  i_font.fromString(config.get(section, option))
  font, ok = QFontDialog.getFont(i_font, parent)
  if ok:
    logger.debug('Font configured for %s.%s: %s' % (section, option, font.toString()))
    if not config.has_section(section):
      config.add_section(section)
    config.set(section, option, font.toString())
    callback(font)
  else:
    logger.debug('Font configuration canceled')


class Config(RawConfigParser):
  
  DEFAULTS = {
      'ui_mainwindow.background_color': '#cccccc',
      'ui_mainwindow.focus_background_color': '#000000',
      'ui_mainwindow.text_width': '400',
      'ui_mainwindow.text_font': 'sans,11,-1,5,50,0,0,0,0,0',
      'ui_mainwindow.text_color': '#000000',
      'ui_mainwindow.text_background_color': '#eeeeee',
      'ui_mainwindow.text_focus_font': 'sans,11,-1,5,50,0,0,0,0,0',
      'ui_mainwindow.text_focus_color': '#00ff00',
      'ui_mainwindow.text_focus_background_color': '#000000',
      }

  def __init__(self, filename, *args, **kwargs):

    RawConfigParser.__init__(self, *args, **kwargs)
    self._filename = filename
    self.read(self._filename)
    self._changed = False
    # Set up delay save
    self._delay_timer = QTimer()
    self._delay_timer.setSingleShot(True)
    QObject.connect(self._delay_timer, SIGNAL("timeout()"), self._delay_save)

  def _has_default(self, section, option):

    return '%s.%s' % (section, option) in self.DEFAULTS

  def _get_default(self, section, option):

    return self.DEFAULTS['%s.%s' % (section, option)]

  def get(self, section, option, default=None):

    try:
      value = RawConfigParser.get(self, section, option)
      logger.debug('Get option %s in section %s, return value: %s' % (option, section, repr(value)))
      return value
    except NoSectionError, e:
      if self._has_default(section, option):
        default = self._get_default(section, option)
        logger.debug('No section %s to get option %s, return default value: %s' % (section, option, repr(default)))
        return default
      else:
        logger.debug('No section %s to get option %s, raise exception' % (section, option))
        raise e
    except NoOptionError, e:
      if self._has_default(section, option):
        default = self._get_default(section, option)
        logger.debug('No %s in section %s, returned default value: %s' % (option, section, repr(default)))
        return default
      else:
        logger.debug('No %s in section %s, raise exception' % (option, section))
        raise e

  def getint(self, section, option, default=None):
  
    return int(self.get(section, option, default))

  def set(self, section, option, value):

    RawConfigParser.set(self, section, option, value)
    self._changed = True
    # Reset the timer
    self._delay_timer.stop()
    self._delay_timer.start(5000)
    logger.debug('C %s.%s = %s, using delay save' % (section, option, repr(value)))

  def _delay_save(self):
    if self._changed:
      # TODO catch
      f = open(self._filename, 'w')
      self.write(f)
      f.close()
      self._changed = False
      logger.debug('Configuration delay-saved')
    else:
      logger.warning('Delay save trigged mistakenly')


config = Config(CONFIG_DIR + '/vorwitor.conf')
