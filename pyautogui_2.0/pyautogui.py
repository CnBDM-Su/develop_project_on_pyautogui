# PyAutoGUI: Cross-platform GUI automation for human beings.
# BSD license
# Al Sweigart al@inventwithpython.com (Send me feedback & suggestions!)
from __future__ import absolute_import, division, print_function

import collections
import sys
import time



import config
from _pyautogui_osx import *


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


class Mouse:
    PAUSE = 0.1  # The number of seconds to pause after EVERY public function call. Useful for debugging.
    FAILSAFE = True
    def __init__(self):
        self.platform_module = Mouse_OS()

        # In seconds. Any duration less than this is rounded to 0.0 to instantly move
        # the mouse.
        self.__MINIMUM_DURATION = 0.1
        # If sleep_amount is too short, time.sleep() will be a no-op and the mouse
        # cursor moves there instantly.
        # TODO: This value should vary with the platform. http://stackoverflow.com/q/1133857
        self.__MINIMUM_SLEEP = 0.05
        self.__PAUSE = 0.1  # The number of seconds to pause after EVERY public function call. Useful for debugging.
        self.__FAILSAFE = True


    # General Functions
    # =================
    def get_point_online(self, x1, y1, x2, y2, n):
        """Returns the (x, y) tuple of the point that has progressed a proportion
        n along the line defined by the two x, y coordinates."""
        x = ((x2 - x1) * n) + x1
        y = ((y2 - y1) * n) + y1
        return x, y


    def linear(self, n):
        """Trivial linear tweening function. """
        if not 0.0 <= n <= 1.0:
            raise ValueError(config.ValueError1)
        return n


    def _auto_pause(self, pause, _pause):
        if _pause:
            if pause is not None:
                time.sleep(pause)
            elif self.__PAUSE != 0:
                time.sleep(self.__PAUSE)


    def _un_pack_xy(self, x, y):
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


    def position(self, x=None, y=None):
        """Returns the current xy coordinates of the mouse cursor as a two-integer tuple."""
        posx, posy = self.platform_module._position
        posx = int(posx)
        posy = int(posy)
        if x is not None:
            posx = int(x)
        if y is not None:
            posy = int(y)
        return posx, posy


    def size(self):
        """Returns the width and height of the screen as a two-integer tuple."""
        return self.platform_module._size


    def on_screen(self, x, y=None):
        """Returns whether the given xy coordinates are on the screen or not."""
        x, y = self._un_pack_xy(x, y)
        x = int(x)
        y = int(y)

        width, height = self.platform_module._size
        return 0 <= x < width and 0 <= y < height


    # Mouse Functions
    # ===============
    def mouse_down(self, x=None, y=None, button=config.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs pressing a mouse button down (but not up)."""
        if button not in (config.LEFT, config.MIDDLE, config.RIGHT, 1, 2, 3):
            raise ValueError("button argument must be one of ('left', 'middle', 'right', 1, 2, 3), not %s" % button)

        self._fail_safe_check()
        x, y = self._un_pack_xy(x, y)
        self._mouse_move_drag(config.MOVE, x, y, 0, 0, duration=0, tween=None)

        x, y = self.platform_module._position # TODO - this isn't right. We need to check the params.
        if button == 1 or str(button).lower() == config.LEFT:
            self.platform_module._mouse_event(x, y, config.LEFT, config.DOWN)
        elif button == 2 or str(button).lower() == config.MIDDLE:
            self.platform_module._mouse_event(x, y, config.MIDDLE, config.DOWN)
        elif button == 3 or str(button).lower() == config.RIGHT:
            self.platform_module._mouse_event(x, y, config.RIGHT, config.DOWN)

        self._auto_pause(pause, _pause)


    def mouse_up(self, x=None, y=None, button=config.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs releasing a mouse button up (but not down beforehand)."""
        if button not in (config.LEFT, config.MIDDLE, config.RIGHT, 1, 2, 3):
            raise ValueError("button argument must be one of ('left', 'middle', 'right', 1, 2, 3), not %s" % button)

        self._fail_safe_check()
        x, y = self._un_pack_xy(x, y)
        self._mouse_move_drag(config.MOVE, x, y, 0, 0, duration=0, tween=None)

        x, y = self.platform_module._position
        if button == 1 or str(button).lower() == config.LEFT:
            self.platform_module._mouse_event(x, y, config.LEFT,config.UP)
        elif button == 2 or str(button).lower() == config.MIDDLE:
            self.platform_module._mouse_event(x, y, config.MIDDLE,config.UP)
        elif button == 3 or str(button).lower() == config.RIGHT:
            self.platform_module._mouse_event(x, y, config.RIGHT,config.UP)

        self._auto_pause(pause, _pause)


    def click(self, x=None, y=None, clicks=1, interval=0.0, button=config.LEFT, duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs pressing a mouse button down and then immediately releasing it."""
        if button not in (config.LEFT, config.MIDDLE, config.RIGHT, 1, 2, 3):
            raise ValueError(config.ValueError)

        self._fail_safe_check()
        x, y = self._un_pack_xy(x, y)
        self._mouse_move_drag(config.MOVE, x, y, 0, 0, duration, tween)

        x, y = self.platform_module._position
        for i in range(clicks):
            self. _fail_safe_check()
            if button == 1 or str(button).lower() == config.LEFT:
                self.platform_module._click(x, y, config.LEFT)
            elif button == 2 or str(button).lower() == config.MIDDLE:
                self.platform_module._click(x, y, config.MIDDLE)
            elif button == 3 or str(button).lower() == config.RIGHT:
                self.platform_module._click(x, y, config.RIGHT)
            else:
                # These mouse buttons for hor. and vert. scrolling only apply to x11:
                self.platform_module._click(x, y, button)

            time.sleep(interval)

        self._auto_pause(pause, _pause)


    def right_click(self, x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs a right mouse button click."""
        self._fail_safe_check()

        self.click(x, y, 1, 0.0, config.RIGHT, _pause=False)

        self._auto_pause(pause, _pause)


    def middle_click(self, x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs a middle mouse button click."""
        self._fail_safe_check()

        self.click(x, y, 1, 0.0, config.MIDDLE, _pause=False)

        self._auto_pause(pause, _pause)


    def double_click(self, x=None, y=None, interval=0.0, button='left', duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs a double click. """
        self._fail_safe_check()

        # Multiple clicks work different in OSX
        if sys.platform == config.OSXPlatform:
            x, y = self._un_pack_xy(x, y)
            self. _mouse_move_drag('move', x, y, 0, 0, duration=0, tween=None)
            x, y = self.platform_module._position
            self.platform_module._multi_click(x, y, button, 2)
        else:
            self.click(x, y, 2, interval, button, _pause=False)

        self._auto_pause(pause, _pause)


    def triple_click(self, x=None, y=None, interval=0.0, button='left', duration=0.0, tween=linear, pause=None, _pause=True):
        """Performs a triple click.."""
        self._fail_safe_check()

        # Multiple clicks work different in OSX
        if sys.platform == config.OSXPlatform:
            x, y = self._un_pack_xy(x, y)
            self._mouse_move_drag(config.MOVE, x, y, 0, 0, duration=0, tween=None)
            x, y = self.platform_module._position
            self.platform_module._multi_click(x, y, button, 3)
        else:
            self.click(x, y, 2, interval, button, _pause=False)
        self._auto_pause(pause, _pause)


    def scroll(self, clicks, x=None, y=None, pause=None, _pause=True):
        """Performs a scroll of the mouse scroll wheel."""
        self._fail_safe_check()
        if type(x) in (tuple, list):
            x, y = x[0], x[1]
        x, y = self.position(x, y)

        self.platform_module._scroll(clicks, x, y)

        self._auto_pause(pause, _pause)


    def h_scroll(self, clicks, x=None, y=None, pause=None, _pause=True):
        """Performs an explicitly horizontal scroll of the mouse scroll wheel,
        if this is supported by the operating system. (Currently just Linux.) """
        self._fail_safe_check()
        if type(x) in (tuple, list):
            x, y = x[0], x[1]
        x, y = self.position(x, y)

        self.platform_module._scroll(clicks, ish=True, x=x, y=y)

        self._auto_pause(pause, _pause)


    def v_scroll(self, clicks, x=None, y=None, pause=None, _pause=True):
        """Performs an explicitly vertical scroll of the mouse scroll wheel,
        if this is supported by the operating system. (Currently just Linux.)"""
        self._fail_safe_check()
        if type(x) in (tuple, list):
            x, y = x[0], x[1]
        x, y = self.position(x, y)
        self.platform_module._scroll(clicks, ish=False, x=x, y=y)

        self._auto_pause(pause, _pause)


    def move_to(self, x=None, y=None, duration=0.0, tween=linear, pause=None, _pause=True):
        """Moves the mouse cursor to a point on the screen."""
        x, y = self._un_pack_xy(x, y)

        self._fail_safe_check()

        self._mouse_move_drag(config.MOVE, x, y, 0, 0, duration, tween)

        self._auto_pause(pause, _pause)


    def move_rel(self, x_offset=None, y_offset=None, duration=0.0, tween=linear, pause=None, _pause=True):
        """Moves the mouse cursor to a point on the screen, relative to its current position."""

        x_offset, y_offset = self._un_pack_xy(x_offset, y_offset)

        self._fail_safe_check()

        self._mouse_move_drag(config.MOVE, None, None, x_offset, y_offset, duration, tween)

        self._auto_pause(pause, _pause)


    def drag_to(self, x=None, y=None, duration=0.0, tween=linear, button=config.LEFT, pause=None, _pause=True, mouseDownUp=True):
        """Performs a mouse drag (mouse movement while a button is held down) to a point on the screen."""
        self._fail_safe_check()
        if type(x) in (tuple, list):
            x, y = x[0], x[1]
        if mouseDownUp:
            self.mouse_down(button=button, _pause=False)
        self._mouse_move_drag(config.DRAG, x, y, 0, 0, duration, tween, button)
        if mouseDownUp:
            self.mouse_up(button=button, _pause=False)

        self._auto_pause(pause, _pause)


    def drag_rel(self, x_offset=0, y_offset=0, duration=0.0, tween=linear, button=config.LEFT, pause=None, _pause=True, mouseDownUp=True):
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

        self._fail_safe_check()

        mousex, mousey = self.platform_module._position
        if mouseDownUp:
            self.mouse_down(button=button, _pause=False)
        self._mouse_move_drag(config.DRAG, mousex, mousey, x_offset, y_offset, duration, tween, button)
        if mouseDownUp:
            self.mouse_up(button=button, _pause=False)

        self._auto_pause(pause, _pause)


    def _mouse_move_drag(self, move_or_drag, x, y, x_offset, y_offset, duration, tween=linear, button=None):
        """Handles the actual move or drag event, since different platforms
        implement them differently."""

        assert move_or_drag in (config.MOVE, config.DRAG), "move_or_drag must be in ('move', 'drag'), not %s" % (move_or_drag)

        if sys.platform != config.OSXPlatform:
            move_or_drag = config.MOVE # Only OS X needs the drag event specifically.

        x_offset = int(x_offset) if x_offset is not None else 0
        y_offset = int(y_offset) if y_offset is not None else 0

        if x is None and y is None and x_offset == 0 and y_offset == 0:
            return  # Special case for no mouse movement at all.

        startx, starty = self.position()

        x = int(x) if x is not None else startx
        y = int(y) if y is not None else starty

        # x, y, x_offset, y_offset are now int.
        x += x_offset
        y += y_offset

        width, height = self.size()

        # Make sure x and y are within the screen bounds.
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))

        # If the duration is small enough, just move the cursor there instantly.
        steps = [(x, y)]

        if duration > self.__MINIMUM_DURATION:
            # Non-instant moving/dragging involves tweening:
            num_steps = max(width, height)
            sleep_amount = duration / num_steps
            if sleep_amount < self.__MINIMUM_SLEEP:
                num_steps = int(duration / self.__MINIMUM_SLEEP)
                sleep_amount = duration / num_steps

            steps = [
                self.get_point_online(startx, starty, x, y, tween(n / num_steps))
                for n in range(num_steps)
            ]
            # Making sure the last position is the actual destination.
            steps.append((x, y))

        for tweenX, tweenY in steps:
            if len(steps) > 1:
                # A single step does not require tweening.
                time.sleep(sleep_amount)

            self._fail_safe_check()
            tweenX = int(round(tweenX))
            tweenY = int(round(tweenY))
            if move_or_drag == config.MOVE:
                self.platform_module._move_to(tweenX, tweenY)
            elif move_or_drag == config.DRAG:
                self.platform_module._drag_to(tweenX, tweenY, button)
            else:
                raise NotImplementedError(config.NotImplementedError.format(move_or_drag))

        self._fail_safe_check()



    def _fail_safe_check(self):
        if self.__FAILSAFE and self.position() == (0, 0):
            raise FailSafeException(config.FailSafeException)

    def display_mouse_position(self,xOffset=0, yOffset=0):
        """This function is meant to be run from the command line. It will
        automatically display the location and RGB of the mouse cursor."""
        print('Press Ctrl-C to quit.')
        if xOffset != 0 or yOffset != 0:
            print('xOffset: %s yOffset: %s' % (xOffset, yOffset))
        resolution = self.size()
        try:
            while True:
                # Get and print the mouse coordinates.
                x, y = self.position()
                positionStr = 'X: ' + str(x - xOffset).rjust(4) + ' Y: ' + str(y - yOffset).rjust(4)
                if (x - xOffset) < 0 or (y - yOffset) < 0 or (x - xOffset) >= resolution[0] or (y - yOffset) >= \
                        resolution[1]:
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

class FailSafeException(Exception):
    pass



