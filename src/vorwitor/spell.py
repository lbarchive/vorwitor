from PyQt4.QtGui import QTextCharFormat, QTextCursor

from enchant.checker import SpellChecker
import enchant

from vorwitor.logger import logger


checker = SpellChecker("en_US")
single_checker = enchant.Dict("en_US")

def hook_textChanged(text):
 
  if not text.updatesEnabled():
    # Should be in processing
    return
  
  # TODO catch for the next
  text.setUpdatesEnabled(False)

  content = unicode(text.toPlainText())
  
  cursor = text.textCursor()
  original_pos = cursor.position()
 
  # TODO
  char_fmt = QTextCharFormat()
  char_fmt.setFont(text.font()) 
 
  # First time or may just copy/delete a lot at once
  if not hasattr(text, 'previous_length') or \
      abs(len(content) - text.previous_length) > 1:
    logger.debug('Spell check: All')
    left_bound = 0
    right_bound = len(content)
  else:
    logger.debug('Spell check: small piece')
    # Just one character added or deleted, or just replaced
    lb1 = content.rfind(' ', 0, original_pos)
    lb2 = content.rfind('\n', 0, original_pos)
    if lb1 == -1 and lb2 == -1:
      left_bound = -1
    elif lb1 == -1:
      left_bound = lb2
    elif lb2 == -1:
      left_bound = lb1
    else:
      left_bound = max(lb1, lb2)

    rb1 = content.find(' ', original_pos)
    rb2 = content.find('\n', original_pos)
    if rb1 == -1 and rb2 == -1:
      right_bound = -1
    elif rb1 == -1:
      right_bound = rb2
    elif rb2 == -1:
      right_bound = rb1
    else:
      right_bound = min(rb1, rb2)

    if left_bound == -1:
      left_bound = 0
    if right_bound == -1:
      right_bound = len(content)

  logger.debug('Check region: %d, %d' % (left_bound, right_bound))
  # Clean check region first
  cursor.setPosition(left_bound)
  cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, right_bound - left_bound)
  text.setTextCursor(cursor)
  char_fmt.setFontUnderline(True)
  char_fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
  text.setCurrentCharFormat(char_fmt)

  # Checking
  checker.set_text(content[left_bound:right_bound])
  for err in checker:
    word = err.word
    logger.debug('Bad word: %s' % word)
    start = left_bound
    while True:
      index = content.find(word, start)
      if index == -1 or index >= right_bound:
        break
      logger.debug(' at position %d' % index)
      cursor.setPosition(index)
      cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))
      text.setTextCursor(cursor)
      char_fmt.setFontUnderline(True)
      char_fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
      text.setCurrentCharFormat(char_fmt)
      start = index + len(word)

  # Restore cursor and reset format
  cursor.setPosition(original_pos)
  text.setTextCursor(cursor)
  char_fmt.setFontUnderline(True)
  char_fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
  text.setCurrentCharFormat(char_fmt)
  
  # Update the previous length for incremental checking
  text.previous_length = len(content)

  text.setUpdatesEnabled(True)

def hook_get_suggestion(text):

  cursor = text.textCursor()
  pos = cursor.position()
  
  cursor.setPosition(pos)
  cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
  cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
  fmt = cursor.charFormat()
  if fmt.underlineStyle() == QTextCharFormat.SpellCheckUnderline:
    word = unicode(cursor.selectedText())
    logger.debug('Got a bad word: %s' % word)
    return single_checker.suggest(word)

def hook_correct_word(text, word):

  logger.debug('Replacing with %s' % word)
  text.setUpdatesEnabled(False)

  cursor = text.textCursor()
  pos = cursor.position()
  
  cursor.setPosition(pos)
  cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
  cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
  
  char_fmt = QTextCharFormat()
  char_fmt.setFont(text.font()) 
  char_fmt.setFontUnderline(True)
  char_fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
  cursor.insertText(word, char_fmt)
  
  # Update the previous length for incremental checking
  text.previous_length = len(text.toPlainText())

  text.setUpdatesEnabled(True)
