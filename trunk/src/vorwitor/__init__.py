from os import makedirs, path
import logging

  
CONFIG_DIR = path.expanduser('~/.vorwitor')
if not path.exists(CONFIG_DIR):
  # Should be first-time user
  makedirs(CONFIG_DIR)


def initialize():
  '''Initials environment for Vorwitor
  
  Configuration, directories, files.
  '''

  # Check configuration directory
    # TODO rest of initialization tasks

  # Load configuration

  # Initialize logger

