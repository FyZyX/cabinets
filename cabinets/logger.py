import logging
import os
import sys

import colorama


COLORS = {
    'BLACK': colorama.Fore.BLACK,
    'RED': colorama.Fore.RED,
    'GREEN': colorama.Fore.GREEN,
    'YELLOW': colorama.Fore.YELLOW,
    'BLUE': colorama.Fore.BLUE,
    'MAGENTA': colorama.Fore.MAGENTA,
    'CYAN': colorama.Fore.CYAN,
    'WHITE': colorama.Fore.WHITE,
    'RESET': colorama.Fore.RESET,
}

# Set up stdout logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
level = logging.getLevelName(LOG_LEVEL)

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s: %(message)s",
                    level=level)

LOGGER_NAME = os.environ.get('LOGGER_NAME', __package__)


def style(*msgs, color=None):
    msg = ' '.join([str(msg) for msg in msgs])
    if not color:
        return msg
    else:
        return f'{COLORS[color.upper()]}' + msg + str(COLORS['RESET'])


def debug(*msgs, color=None, name=None):
    logger = logging.getLogger(name or LOGGER_NAME)
    logger.debug(style(*msgs, color=color))


def info(*msgs, color=None, name=None):
    logger = logging.getLogger(name or LOGGER_NAME)
    logger.info(style(*msgs, color=color))


def log(*msgs, color=None, name=None):
    info(*msgs, color=color, name=name)


def warning(*msgs, color=None, name=None):
    logger = logging.getLogger(name or LOGGER_NAME)
    logger.warning(style(*msgs, color=color))


def error(*msgs, color='red', name=None):
    logger = logging.getLogger(name or LOGGER_NAME)
    logger.error(style(*msgs, color=color))


def exception(*msgs, color='red', name=None):
    logger = logging.getLogger(name or LOGGER_NAME)
    logger.exception(style(*msgs, color=color))
