# PyAutoGUI: Cross-platform GUI automation for human beings.
# BSD license
# Al Sweigart al@inventwithpython.com (Send me feedback & suggestions!)

"""
IMPORTANT NOTE!

To use this module on Mac OS X, you need the PyObjC module installed.
For Python 3, run:
    sudo pip3 install pyobjc-core
    sudo pip3 install pyobjc
For Python 2, run:
    sudo pip install pyobjc-core
    sudo pip install pyobjc
(There's some bug with their installer, so install pyobjc-core first or else
the install takes forever.)

To use this module on Linux, you need Xlib module installed.
For Python 3, run:
    sudo pip3 install python3-Xlib
For Python 2, run:
    sudo pip install Xlib

To use this module on Windows, you do not need anything else.

You will need PIL/Pillow to use the screenshot features.
"""

import collections
import sys
import time

from __future__ import absolute_import, division, print_function

from pyautogui import dataClass

'''__version__ = '0.9.37'''

try:
    import pytweening
    from pytweening import (easeInQuad, easeOutQuad, easeInOutQuad,
        easeInCubic, easeOutCubic, easeInOutCubic, easeInQuart, easeOutQuart,
        easeInOutQuart, easeInQuint, easeOutQuint, easeInOutQuint, easeInSine,
        easeOutSine, easeInOutSine, easeInExpo, easeOutExpo, easeInOutExpo,
        easeInCirc, easeOutCirc, easeInOutCirc, easeInElastic, easeOutElastic,
        easeInOutElastic, easeInBack, easeOutBack, easeInOutBack, easeInBounce,
        easeOutBounce, easeInOutBounce)
    # getLine is not needed.
    # getPointOnLine has been redefined in this file, to avoid dependency on pytweening.
    # linear has also been redefined in this file.
except ImportError:
    pass

try:
    import pymsgbox
    from pymsgbox import alert, confirm, prompt, password

except ImportError:
    # If pymsgbox module is not found, those methods will not be available.
    pass


try:
    from pyscreeze import screenshot
    from pyscreeze import (center, grab, locate, locateAll, locateAllOnScreen,
        locateCenterOnScreen, locateOnScreen, pixel, pixelMatchesColor,
        screenshot)

except ImportError:
    # If pyscreeze module is not found, screenshot-related features will simply
    # not work.
    pass

'''
KEY_NAMES = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
     ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
     '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
     'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
     'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
     'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
     'browserback', 'browserfavorites', 'browserforward', 'browserhome',
     'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
     'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
     'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
     'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
     'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
     'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
     'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
     'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
     'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
     'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
     'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
     'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
     'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
     'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
     'command', 'option', 'optionleft', 'optionright']
     '''
'''KEYBOARD_KEYS = dataClass.KEY_NAMES  ''' # keeping old KEYBOARD_KEYS for backwards compatibility


# 如果关键字符为大写或回车，则返回True。
def is_shift_character(character):
    """Returns True if the key character is uppercase or shifted."""
    return character.isupper() or character in dataClass.character


# 决定平台
# The platformModule is where we reference the platform-specific functions.
if sys.platform.startswith(dataClass.JAVAPlatform):
    #from . import _pyautogui_java as platformModule
    raise NotImplementedError('Jython is not yet supported by PyAutoGUI.')

elif sys.platform == dataClass.OSXPlatform:
    from . import _pyautogui_osx as platform_module
elif sys.platform == dataClass.WINPlatform:
    from . import _pyautogui_win as platform_module
    from ._window_win import Window, getWindows, getWindow
else:
    from . import _pyautogui_x11 as platform_module


# TODO: Having module-wide user-writable global variables is bad. It makes
# restructuring the code very difficult. For instance, what if we decide to
# move the mouse-related functions to a separate file (a submodule)? How that
# file will access this module vars? It will probably lead to a circular
# import.

# In seconds. Any duration less than this is rounded to 0.0 to instantly move
# the mouse.
MINIMUM_DURATION = 0.1
# If sleep_amount is too short, time.sleep() will be a no-op and the mouse
# cursor moves there instantly.
# TODO: This value should vary with the platform. http://stackoverflow.com/q/1133857
MINIMUM_SLEEP = 0.05
PAUSE = 0.1 # The number of seconds to pause after EVERY public function call. Useful for debugging.
FAILSAFE = True


# General Functions
# =================
def get_point_online(x1, y1, x2, y2, n):
    """Returns the (x, y) tuple of the point that has progressed a proportion
    n along the line defined by the two x, y coordinates."""
    x = ((x2 - x1) * n) + x1
    y = ((y2 - y1) * n) + y1
    return x, y


def linear(n):
    """Trivial linear tweening function. """
    if not 0.0 <= n <= 1.0:
        raise ValueError(dataClass.ValueError1)
    return n


def _auto_pause(pause, _pause):
    if _pause:
        if pause is not None:
            time.sleep(pause)
        elif PAUSE != 0:
            time.sleep(PAUSE)


def _un_pack_xy(x, y):
    """If x is a sequence and y is None, returns x[0], y[0]. Else, returns x, y."""
    if isinstance(x, collections.Sequence):
        if len(x) == 2:
            if y is None:
                x, y = x
            else:
                raise ValueError('When passing a sequence at the x argument, the y argument must not be passed (received {0}).'.format(repr(y)))
        else:
            raise ValueError('The supplied sequence must have exactly 2 elements ({0} were received).'.format(len(x)))
    else:
        pass

    return x, y


def position(x=None, y=None):
    """Returns the current xy coordinates of the mouse cursor as a two-integer tuple."""
    posx, posy = platform_module._position()
    posx = int(posx)
    posy = int(posy)
    if x is not None:
        posx = int(x)
    if y is not None:
        posy = int(y)
    return posx, posy


def size():
    """Returns the width and height of the screen as a two-integer tuple."""
    return platform_module._size()


def on_screen(x, y=None):
    """Returns whether the given xy coordinates are on the screen or not."""
    x, y = _un_pack_xy(x, y)
    x = int(x)
    y = int(y)

    width, height = platform_module._size()
    return 0 <= x < width and 0 <= y < height


# Mouse Functions
# ===============
def mouse_down(x=None, y=None, button=dataClass.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs pressing a mouse button down (but not up)."""
    if button not in (dataClass.LEFT, dataClass.MIDDLE, dataClass.RIGHT, 1, 2, 3):
        raise ValueError("button argument must be one of ('left', 'middle', 'right', 1, 2, 3), not %s" % button)

    _fail_safe_check()
    x, y = _un_pack_xy(x, y)
    _mouse_move_drag(dataClass.MOVE, x, y, 0, 0, duration=0, tween=None)

    x, y = platform_module._position() # TODO - this isn't right. We need to check the params.
    if button == 1 or str(button).lower() == dataClass.LEFT:
        platform_module._mouse_down(x, y, dataClass.LEFT)
    elif button == 2 or str(button).lower() == dataClass.MIDDLE:
        platform_module._mouse_down(x, y, dataClass.MIDDLE)
    elif button == 3 or str(button).lower() == dataClass.RIGHT:
        platform_module._mouse_down(x, y, dataClass.RIGHT)

    _auto_pause(pause, _pause)


def mouse_up(x=None, y=None, button=dataClass.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs releasing a mouse button up (but not down beforehand)."""
    if button not in (dataClass.LEFT, dataClass.MIDDLE, dataClass.RIGHT, 1, 2, 3):
        raise ValueError("button argument must be one of ('left', 'middle', 'right', 1, 2, 3), not %s" % button)

    _fail_safe_check()
    x, y = _un_pack_xy(x, y)
    _mouse_move_drag(dataClass.MOVE, x, y, 0, 0, duration=0, tween=None)

    x, y = platform_module._position()
    if button == 1 or str(button).lower() == dataClass.LEFT:
        platform_module._mouse_up(x, y, dataClass.LEFT)
    elif button == 2 or str(button).lower() == dataClass.MIDDLE:
        platform_module._mouse_up(x, y, dataClass.MIDDLE)
    elif button == 3 or str(button).lower() == dataClass.RIGHT:
        platform_module._mouse_up(x, y, dataClass.RIGHT)

    _auto_pause(pause, _pause)


def click(x=None, y=None, clicks=1, interval=0.0, button=dataClass.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs pressing a mouse button down and then immediately releasing it."""
    if button not in (dataClass.LEFT, dataClass.MIDDLE, dataClass.RIGHT, 1, 2, 3):
        raise ValueError(dataClass.ValueError)

    _fail_safe_check()
    x, y = _un_pack_xy(x, y)
    _mouse_move_drag(dataClass.MOVE, x, y, 0, 0, duration, tween)

    x, y = platform_module._position()
    for i in range(clicks):
        _fail_safe_check()
        if button == 1 or str(button).lower() == dataClass.LEFT:
            platform_module._click(x, y, dataClass.LEFT)
        elif button == 2 or str(button).lower() == dataClass.MIDDLE:
            platform_module._click(x, y, dataClass.MIDDLE)
        elif button == 3 or str(button).lower() == dataClass.RIGHT:
            platform_module._click(x, y, dataClass.RIGHT)
        else:
            # These mouse buttons for hor. and vert. scrolling only apply to x11:
            platform_module._click(x, y, button)

        time.sleep(interval)

    _auto_pause(pause, _pause)


def right_click(x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs a right mouse button click."""
    _fail_safe_check()

    click(x, y, 1, 0.0, dataClass.RIGHT, _pause=False)

    _auto_pause(pause, _pause)


def middle_click(x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs a middle mouse button click."""
    _fail_safe_check()

    click(x, y, 1, 0.0, dataClass.MIDDLE, _pause=False)

    _auto_pause(pause, _pause)


def double_click(x=None, y=None, interval=0.0, button='left', duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs a double click. """
    _fail_safe_check()

    # Multiple clicks work different in OSX
    if sys.platform == dataClass.OSXPlatform:
        x, y = _un_pack_xy(x, y)
        _mouse_move_drag('move', x, y, 0, 0, duration=0, tween=None)
        x, y = platform_module._position()
        platform_module._multi_click(x, y, button, 2)
    else:
        click(x, y, 2, interval, button, _pause=False)

    _auto_pause(pause, _pause)


def triple_click(x=None, y=None, interval=0.0, button='left', duration=0.0, tween=linear, pause=None, _pause=True):
    """Performs a triple click.."""
    _fail_safe_check()

    # Multiple clicks work different in OSX
    if sys.platform == dataClass.OSXPlatform:
        x, y = _un_pack_xy(x, y)
        _mouse_move_drag(dataClass.MOVE, x, y, 0, 0, duration=0, tween=None)
        x, y = platform_module._position()
        platform_module._multi_click(x, y, button, 3)
    else:
        click(x, y, 2, interval, button, _pause=False)
    _auto_pause(pause, _pause)


def scroll(clicks, x=None, y=None, pause=None, _pause=True):
    """Performs a scroll of the mouse scroll wheel."""
    _fail_safe_check()
    if type(x) in (tuple, list):
        x, y = x[0], x[1]
    x, y = position(x, y)

    platform_module._scroll(clicks, x, y)

    _auto_pause(pause, _pause)


def h_scroll(clicks, x=None, y=None, pause=None, _pause=True):
    """Performs an explicitly horizontal scroll of the mouse scroll wheel,
    if this is supported by the operating system. (Currently just Linux.) """
    _fail_safe_check()
    if type(x) in (tuple, list):
        x, y = x[0], x[1]
    x, y = position(x, y)

    platform_module._h_scroll(clicks, x, y)

    _auto_pause(pause, _pause)


def v_scroll(clicks, x=None, y=None, pause=None, _pause=True):
    """Performs an explicitly vertical scroll of the mouse scroll wheel,
    if this is supported by the operating system. (Currently just Linux.)"""
    _fail_safe_check()
    if type(x) in (tuple, list):
        x, y = x[0], x[1]
    x, y = position(x, y)
    platform_module._v_scroll(clicks, x, y)

    _auto_pause(pause, _pause)


def move_to(x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
    """Moves the mouse cursor to a point on the screen."""
    x, y = _un_pack_xy(x, y)

    _fail_safe_check()

    _mouse_move_drag(dataClass.MOVE, x, y, 0, 0, duration, tween)

    _auto_pause(pause, _pause)


def move_rel(x_offset=None, y_offset=None, duration=0.0, tween=linear, pause=None, _pause=True):
    """Moves the mouse cursor to a point on the screen, relative to its current position."""

    x_offset, y_offset = _un_pack_xy(x_offset, y_offset)

    _fail_safe_check()

    _mouse_move_drag(dataClass.MOVE, None, None, x_offset, y_offset, duration, tween)

    _auto_pause(pause, _pause)


def drag_to(x=None, y=None, duration=0.0, tween=linear, button=dataClass.LEFT, pause=None, _pause=True, mouseDownUp=True):
    """Performs a mouse drag (mouse movement while a button is held down) to a point on the screen."""
    _fail_safe_check()
    if type(x) in (tuple, list):
        x, y = x[0], x[1]
    if mouseDownUp:
        mouse_down(button=button, _pause=False)
    _mouse_move_drag(dataClass.DRAG, x, y, 0, 0, duration, tween, button)
    if mouseDownUp:
        mouse_up(button=button, _pause=False)

    _auto_pause(pause, _pause)


def drag_rel(x_offset=0, y_offset=0, duration=0.0, tween=linear, button=dataClass.LEFT, pause=None, _pause=True, mouseDownUp=True):
    """Performs a mouse drag (mouse movement while a button is held down) to a
    point on the screen, relative to its current position."""
    if x_offset is None:
        x_offset = 0
    if y_offset is None:
        y_offset = 0

    if type(x_offset) in (tuple, list):
        x_offset, y_offset = x_offset[0], x_offset[1]

    if x_offset == 0 and y_offset == 0:
        return # no-op case

    _fail_safe_check()

    mousex, mousey = platform_module._position()
    if mouseDownUp:
        mouse_down(button=button, _pause=False)
    _mouse_move_drag(dataClass.DRAG, mousex, mousey, x_offset, y_offset, duration, tween, button)
    if mouseDownUp:
        mouse_up(button=button, _pause=False)

    _auto_pause(pause, _pause)


def _mouse_move_drag(move_or_drag, x, y, x_offset, y_offset, duration, tween=linear, button=None):
    """Handles the actual move or drag event, since different platforms
    implement them differently."""

    assert move_or_drag in (dataClass.MOVE, dataClass.DRAG), "move_or_drag must be in ('move', 'drag'), not %s" % (move_or_drag)

    if sys.platform != dataClass.OSXPlatform:
        move_or_drag = dataClass.MOVE # Only OS X needs the drag event specifically.

    x_offset = int(x_offset) if x_offset is not None else 0
    y_offset = int(y_offset) if y_offset is not None else 0

    if x is None and y is None and x_offset == 0 and y_offset == 0:
        return  # Special case for no mouse movement at all.

    startx, starty = position()

    x = int(x) if x is not None else startx
    y = int(y) if y is not None else starty

    # x, y, x_offset, y_offset are now int.
    x += x_offset
    y += y_offset

    width, height = size()

    # Make sure x and y are within the screen bounds.
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))

    # If the duration is small enough, just move the cursor there instantly.
    steps = [(x, y)]

    if duration > MINIMUM_DURATION:
        # Non-instant moving/dragging involves tweening:
        num_steps = max(width, height)
        sleep_amount = duration / num_steps
        if sleep_amount < MINIMUM_SLEEP:
            num_steps = int(duration / MINIMUM_SLEEP)
            sleep_amount = duration / num_steps

        steps = [
            get_point_online(startx, starty, x, y, tween(n / num_steps))
            for n in range(num_steps)
        ]
        # Making sure the last position is the actual destination.
        steps.append((x, y))

    for tweenX, tweenY in steps:
        if len(steps) > 1:
            # A single step does not require tweening.
            time.sleep(sleep_amount)

        _fail_safe_check()
        tweenX = int(round(tweenX))
        tweenY = int(round(tweenY))
        if move_or_drag == dataClass.MOVE:
            platform_module._move_to(tweenX, tweenY)
        elif move_or_drag == dataClass.DRAG:
            platform_module._drag_to(tweenX, tweenY, button)
        else:
            raise NotImplementedError(dataClass.NotImplementedError.format(move_or_drag))

    _fail_safe_check()

'''
# Keyboard Functions
# ==================

def isValidKey(key):
    """Returns a Boolean value if the given key is a valid value to pass to
    PyAutoGUI's keyboard-related functions for the current platform.

    This function is here because passing an invalid value to the PyAutoGUI
    keyboard functions currently is a no-op that does not raise an exception.

    Some keys are only valid on some platforms. For example, while 'esc' is
    valid for the Escape key on all platforms, 'browserback' is only used on
    Windows operating systems.

    Args:
      key (str): The key value.

    Returns:
      bool: True if key is a valid value, False if not.
    """
    return platformModule.keyboardMapping.get(key, None) != None


# 键盘按下没有释放
def keyDown(key, pause=None, _pause=True):
    """Performs a keyboard key press without the release. This will put that
    key in a held down state.

    NOTE: For some reason, this does not seem to cause key repeats like would
    happen if a keyboard key was held down on a text field.

    Args:
      key (str): The key to be pressed down. The valid names are listed in
      KEYBOARD_KEYS.

    Returns:
      None
    """
    if len(key) > 1:
        key = key.lower()

    _failSafeCheck()
    platformModule._keyDown(key)

    _autoPause(pause, _pause)


# 键盘释放（没有事先按下？？）
def keyUp(key, pause=None, _pause=True):
    """Performs a keyboard key release (without the press down beforehand).

    Args:
      key (str): The key to be released up. The valid names are listed in
      KEYBOARD_KEYS.

    Returns:
      None
    """
    if len(key) > 1:
        key = key.lower()

    _failSafeCheck()
    platformModule._keyUp(key)

    _autoPause(pause, _pause)


# 键盘按下，然后按下释放（空格？？）键。
def press(keys, presses=1, interval=0.0, pause=None, _pause=True):
    """Performs a keyboard key press down, followed by a release.
    Args:
      key (str, list): The key to be pressed. The valid names are listed in
      KEYBOARD_KEYS. Can also be a list of such strings.
      按下键盘，按下的字符串会列在KEYBOARD_KEYS中，变成字符串列表。
      presses (integer, optiional): the number of press repetition
      1 by default, for just one press
      默认情况下按下重复次数1，仅按一次
      interval (float, optional): How many seconds between each press.
      0.0 by default, for no pause between presses.
      默认情况下每次按下0.0之间的秒数，按下之间没有暂停。
      pause (float, optional): How many seconds in the end of function process.
      None by default, for no pause in the end of function process.
      完成输入之后的停顿的时间，一般没有暂停键。
    Returns:
      None
    """
    """如果输入的是字符串，存入数组
       其他情况：一个一个按下这些key
    """
    if type(keys) == str:
       keys = [keys] # put string in a list
    else:
        lowerKeys = []
        for s in keys:
            if len(s) > 1:
                lowerKeys.append(s.lower())
            else:
                lowerKeys.append(s)
    interval = float(interval)
    for i in range(presses):
        for k in keys:
            _failSafeCheck()
            platformModule._keyDown(k)
            platformModule._keyUp(k)
        time.sleep(interval)

    _autoPause(pause, _pause)


#对于消息中的每个字符，按下键盘键，然后按下空格键。
def typewrite(message, interval=0.0, pause=None, _pause=True):
    """
     message参数也可以是字符串列表，在这种情况下，可以使用任何有效的键盘名称。

     由于这会执行一系列键盘按下而不按住键，因此不能用于执行键盘快捷键。 使用 hotkey()函数。

    hotkey()：对按顺序传递的参数执行按键按下，然后按相反顺序执行键释放。

    Performs a keyboard key press down, followed by a release, for each of
    the characters in message.

    The message argument can also be list of strings, in which case any valid
    keyboard name can be used.

    Since this performs a sequence of keyboard presses and does not hold down
    keys, it cannot be used to perform keyboard shortcuts. Use the hotkey()
    function for that.

    Args:
      message (str, list): If a string, then the characters to be pressed. If a
        list, then the key names of the keys to press in order. The valid names
        are listed in KEYBOARD_KEYS.
      interval (float, optional): The number of seconds in between each press.
        0.0 by default, for no pause in between presses.

    Returns:
      None
    """
    interval = float(interval)

    _failSafeCheck()

    for c in message:
        if len(c) > 1:
            c = c.lower()
        press(c, _pause=False)
        time.sleep(interval)
        _failSafeCheck()

    _autoPause(pause, _pause)


# 快捷键
def hotkey(*args, **kwargs):
    """Performs key down presses on the arguments passed in order, then performs
    key releases in reverse order.
    对按顺序传递的参数执行按键按下，然后按相反顺序执行键释放。

    The effect is that calling hotkey('ctrl', 'shift', 'c') would perform a
    "Ctrl-Shift-C" hotkey/keyboard shortcut press.

    Args:
      key(s) (str): The series of keys to press, in order. This can also be a
        list of key strings to press.
      interval (float, optional): The number of seconds in between each press.
        0.0 by default, for no pause in between presses.

    Returns:
      None
    """
    interval = float(kwargs.get('interval', 0.0))

    _failSafeCheck()

    for c in args:
        if len(c) > 1:
            c = c.lower()
        platformModule._keyDown(c)
        time.sleep(interval)
    for c in reversed(args):
        if len(c) > 1:
            c = c.lower()
        platformModule._keyUp(c)
        time.sleep(interval)

    _autoPause(kwargs.get('pause', None), kwargs.get('_pause', True))

'''


class FailSafeException(Exception):
    pass


def _fail_safe_check():
    if FAILSAFE and position() == (0, 0):
        raise FailSafeException(dataClass.FailSafeException)


def display_mouse_position(xOffset=0, yOffset=0):
    """This function is meant to be run from the command line. It will
    automatically display the location and RGB of the mouse cursor."""
    print('Press Ctrl-C to quit.')
    if xOffset != 0 or yOffset != 0:
        print('xOffset: %s yOffset: %s' % (xOffset, yOffset))
    resolution = size()
    try:
        while True:
            # Get and print the mouse coordinates.
            x, y = position()
            positionStr = 'X: ' + str(x - xOffset).rjust(4) + ' Y: ' + str(y - yOffset).rjust(4)
            if (x - xOffset) < 0 or (y - yOffset) < 0 or (x - xOffset) >= resolution[0] or (y - yOffset) >= resolution[1]:
                pixelColor = ('NaN', 'NaN', 'NaN')
            else:
                pixelColor = screenshot().getpixel((x, y))
            positionStr += ' RGB: (' + str(pixelColor[0]).rjust(3)
            positionStr += ', ' + str(pixelColor[1]).rjust(3)
            positionStr += ', ' + str(pixelColor[2]).rjust(3) + ')'
            sys.stdout.write(positionStr)
            sys.stdout.write('\b' * len(positionStr))
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        sys.stdout.flush()
