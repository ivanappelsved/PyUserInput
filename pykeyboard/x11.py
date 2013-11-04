#Copyright 2013 Paul Barton
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input
from Xlib.ext import record
from Xlib.protocol import rq
import Xlib.XK


from .base import PyKeyboardMeta, PyKeyboardEventMeta

import time

special_X_keysyms = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Return",  # for some reason this needs to be cr, not lf
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
    }

class PyKeyboard(PyKeyboardMeta):
    """
    The PyKeyboard implementation for X11 systems (mostly linux). This
    allows one to simulate keyboard input.
    """
    def __init__(self, display=None):
        PyKeyboardMeta.__init__(self)
        self.display = Display(display)
        self.display2 = Display(display)
        self.special_key_assignment()

    def press_key(self, character=''):
        """
        Press a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        try:  # Detect uppercase or shifted character
            shifted = self.is_char_shifted(character)
        except AttributeError:  # Handle the case of integer keycode argument
            fake_input(self.display, X.KeyPress, character)
            self.display.sync()
        else:
            if shifted:
                fake_input(self.display, X.KeyPress, self.shift_key)
            keycode = self.lookup_character_keycode(character)
            fake_input(self.display, X.KeyPress, keycode)
            self.display.sync()

    def release_key(self, character=''):
        """
        Release a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        try:  # Detect uppercase or shifted character
            shifted = self.is_char_shifted(character)
        except AttributeError:  # Handle the case of integer keycode argument
            fake_input(self.display, X.KeyRelease, character)
            self.display.sync()
        else:
            if shifted:
                fake_input(self.display, X.KeyRelease, self.shift_key)
            keycode = self.lookup_character_keycode(character)
            fake_input(self.display, X.KeyRelease, keycode)
            self.display.sync()

    def special_key_assignment(self):
        """
        Determines the keycodes for common special keys on the keyboard. These
        are integer values and can be passed to the other key methods.
        Generally speaking, these are non-printable codes.
        """
        #This set of keys compiled using the X11 keysymdef.h file as reference
        #They comprise a relatively universal set of keys, though there may be
        #exceptions which may come up for other OSes and vendors. Countless
        #special cases exist which are not handled here, but may be extended.
        #TTY Function Keys
        self.backspace_key = self.lookup_character_keycode('BackSpace')
        self.tab_key = self.lookup_character_keycode('Tab')
        self.linefeed_key = self.lookup_character_keycode('Linefeed')
        self.clear_key = self.lookup_character_keycode('Clear')
        self.return_key = self.lookup_character_keycode('Return')
        self.enter_key = self.return_key  # Because many keyboards call it "Enter"
        self.pause_key = self.lookup_character_keycode('Pause')
        self.scroll_lock_key = self.lookup_character_keycode('Scroll_Lock')
        self.sys_req_key = self.lookup_character_keycode('Sys_Req')
        self.escape_key = self.lookup_character_keycode('Escape')
        self.delete_key = self.lookup_character_keycode('Delete')
        #Modifier Keys
        self.shift_l_key = self.lookup_character_keycode('Shift_L')
        self.shift_r_key = self.lookup_character_keycode('Shift_R')
        self.shift_key = self.shift_l_key  # Default Shift is left Shift
        self.alt_l_key = self.lookup_character_keycode('Alt_L')
        self.alt_r_key = self.lookup_character_keycode('Alt_R')
        self.alt_key = self.alt_l_key  # Default Alt is left Alt
        self.control_l_key = self.lookup_character_keycode('Control_L')
        self.control_r_key = self.lookup_character_keycode('Control_R')
        self.control_key = self.control_l_key  # Default Ctrl is left Ctrl
        self.caps_lock_key = self.lookup_character_keycode('Caps_Lock')
        self.capital_key = self.caps_lock_key  # Some may know it as Capital
        self.shift_lock_key = self.lookup_character_keycode('Shift_Lock')
        self.meta_l_key = self.lookup_character_keycode('Meta_L')
        self.meta_r_key = self.lookup_character_keycode('Meta_R')
        self.super_l_key = self.lookup_character_keycode('Super_L')
        self.windows_l_key = self.super_l_key  # Cross-support; also it's printed there
        self.super_r_key = self.lookup_character_keycode('Super_R')
        self.windows_r_key = self.super_r_key  # Cross-support; also it's printed there
        self.hyper_l_key = self.lookup_character_keycode('Hyper_L')
        self.hyper_r_key = self.lookup_character_keycode('Hyper_R')
        #Cursor Control and Motion
        self.home_key = self.lookup_character_keycode('Home')
        self.up_key = self.lookup_character_keycode('Up')
        self.down_key = self.lookup_character_keycode('Down')
        self.left_key = self.lookup_character_keycode('Left')
        self.right_key = self.lookup_character_keycode('Right')
        self.end_key = self.lookup_character_keycode('End')
        self.begin_key = self.lookup_character_keycode('Begin')
        self.page_up_key = self.lookup_character_keycode('Page_Up')
        self.page_down_key = self.lookup_character_keycode('Page_Down')
        self.prior_key = self.lookup_character_keycode('Prior')
        self.next_key = self.lookup_character_keycode('Next')
        #Misc Functions
        self.select_key = self.lookup_character_keycode('Select')
        self.print_key = self.lookup_character_keycode('Print')
        self.print_screen_key = self.print_key  # Seems to be the same thing
        self.snapshot_key = self.print_key  # Another name for printscreen
        self.execute_key = self.lookup_character_keycode('Execute')
        self.insert_key = self.lookup_character_keycode('Insert')
        self.undo_key = self.lookup_character_keycode('Undo')
        self.redo_key = self.lookup_character_keycode('Redo')
        self.menu_key = self.lookup_character_keycode('Menu')
        self.apps_key = self.menu_key  # Windows...
        self.find_key = self.lookup_character_keycode('Find')
        self.cancel_key = self.lookup_character_keycode('Cancel')
        self.help_key = self.lookup_character_keycode('Help')
        self.break_key = self.lookup_character_keycode('Break')
        self.mode_switch_key = self.lookup_character_keycode('Mode_switch')
        self.script_switch_key = self.lookup_character_keycode('script_switch')
        self.num_lock_key = self.lookup_character_keycode('Num_Lock')
        #Keypad Keys: Dictionary structure
        keypad = ['Space', 'Tab', 'Enter', 'F1', 'F2', 'F3', 'F4', 'Home',
                  'Left', 'Up', 'Right', 'Down', 'Prior', 'Page_Up', 'Next',
                  'Page_Down', 'End', 'Begin', 'Insert', 'Delete', 'Equal',
                  'Multiply', 'Add', 'Separator', 'Subtract', 'Decimal',
                  'Divide', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.keypad_keys = {k: self.lookup_character_keycode('KP_'+str(k)) for k in keypad}
        self.numpad_keys = self.keypad_keys
        #Function Keys/ Auxilliary Keys
        #FKeys
        self.function_keys = [None] + [self.lookup_character_keycode('F'+str(i)) for i in xrange(1,36)]
        #LKeys
        self.l_keys = [None] + [self.lookup_character_keycode('L'+str(i)) for i in xrange(1,11)]
        #RKeys
        self.r_keys = [None] + [self.lookup_character_keycode('R'+str(i)) for i in xrange(1,16)]

        #Unsupported keys from windows
        self.kana_key = None
        self.hangeul_key = None # old name - should be here for compatibility
        self.hangul_key = None
        self.junjua_key = None
        self.final_key = None
        self.hanja_key = None
        self.kanji_key = None
        self.convert_key = None
        self.nonconvert_key = None
        self.accept_key = None
        self.modechange_key = None
        self.sleep_key = None

    def lookup_character_keycode(self, character):
        """
        Looks up the keysym for the character then returns the keycode mapping
        for that keysym.
        """
        keysym = Xlib.XK.string_to_keysym(character)
        if keysym == 0:
            keysym = Xlib.XK.string_to_keysym(special_X_keysyms[character])
        return self.display.keysym_to_keycode(keysym)


class PyKeyboardEvent(PyKeyboardEventMeta):
    """
    The PyKeyboardEvent implementation for X11 systems (mostly linux). This
    allows one to listen for keyboard input.
    """
    def __init__(self, display=None):
        PyKeyboardEventMeta.__init__(self)
        self.display = Display(display)
        self.display2 = Display(display)
        self.ctx = self.display2.record_create_context(
            0,
            [record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.KeyRelease),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }])

        #Set the state and map the bits to initial modifiers
        self.state = 0
        self.modifier_bits = {'Shift': 1, 'Caps_Lock': 2, 'Control': 4,
                              'Mod1': 8, 'Mod2': 16, 'Mod3': 32, 'Mod4': 64,
                              'Mod5': 128, 'Alt': 0, 'Num_Lock': 0, 'Super': 0}

        self.modifiers = {'Shift': 0, 'Caps_Lock': 0, 'Control': 0, 'Mod1': 0,
                          'Mod2': 0, 'Mod3': 0, 'Mod4': 0, 'Mod5': 0, 'Alt': 0,
                          'Num_Lock': 0, 'Super': 0}

        #Should I add Hyper, Meta, or anything else?

        #Get these dictionaries for converting keysyms and strings
        self.keysym_to_string, self.string_to_keysym = self.get_translation_dicts()
        print(self.keysym_to_string)

        #This function will create a dictionary mapping modifiers to keycodes
        #It will also dynamically assign named modifiers to Mod1-5 positions
        self.configure_modifiers()

    def run(self):
        """Begin listening for keyboard input events."""
        self.state = True
        if self.capture:
            self.display2.screen().root.grab_keyboard(True, X.KeyPressMask | X.KeyReleaseMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)

        self.display2.record_enable_context(self.ctx, self.handler)
        self.display2.record_free_context(self.ctx)

    def stop(self):
        """Stop listening for keyboard input events."""
        self.state = False
        self.display.record_disable_context(self.ctx)
        self.display.ungrab_keyboard(X.CurrentTime)
        self.display.flush()
        self.display2.record_disable_context(self.ctx)
        self.display2.ungrab_keyboard(X.CurrentTime)
        self.display2.flush()

    def handler(self, reply):
        """Upper level handler of keyboard events."""
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.display.display, None, None)
            if self.escape(event):  # Quit if this returns True
                self.stop()
            else:
                self._tap(event)

    def _tap(self, event):
        keycode = event.detail
        press_bool = (event.type == X.KeyPress)

        #Detect modifier states from event.state
        for mod, bit in self.modifier_bits.items():
            self.modifiers[mod] = event.state & bit

        if keycode in self.all_mod_keycodes:
            character = self.display.keycode_to_keysym(keycode, 0)
        else:
            character = self.lookup_char_from_keycode(keycode,
                                                      state=event.state)

        #All key events get passed to self.tap()
        self.tap(keycode,
                 character,
                 press=press_bool)

    def lookup_char_from_keycode(self, keycode, state=None):
        """
        This will conduct a lookup of the character or string associated with a
        given keycode. The current keyboard modifier state will be used as a
        default, or an appropriate state may be passed.
        """

        #keycode_to_keysym does not work the way I thought it did...
        keysym = self.display.keycode_to_keysym(keycode, 0)

        #If the character is ascii printable, return that character
        if keysym & 0x7f == keysym and self.ascii_printable(keysym):
            return chr(keysym)

        #If the character was not printable, look for its name
        try:
            char = self.keysym_to_string[keysym]
        except KeyError:
            print('Unable to determine character.')
            print('Keycode: {0} KeySym {1}'.format(keycode, keysym))
            return None
        else:
            return char

    def escape(self, event):
        if event.detail == self.lookup_character_keycode('Escape'):
            return True
        return False

    def configure_modifiers(self):
        """
        This function detects and assigns the keycodes pertaining to the
        keyboard modifiers to their names in a dictionary. This dictionary will
        can be accessed in the following manner:
            self.modifier_keycodes['Shift']  # All keycodes for Shift Masking

        It also assigns certain named modifiers (Alt, Num_Lock, Super), which
        may be dynamically assigned to Mod1 - Mod5 on different platforms. This
        should generally allow the user to do the following lookups on any
        system:
            self.modifier_keycodes['Alt']  # All keycodes for Alt Masking
            self.modifiers['Alt']  # State of Alt mask, non-zero if "ON"
        """
        modifier_mapping = self.display.get_modifier_mapping()
        all_mod_keycodes = []
        mod_keycodes = {}
        mod_index = [('Shift', X.ShiftMapIndex), ('Caps_Lock', X.LockMapIndex),
                     ('Control', X.ControlMapIndex), ('Mod1', X.Mod1MapIndex),
                     ('Mod2', X.Mod2MapIndex), ('Mod3', X.Mod3MapIndex),
                     ('Mod4', X.Mod4MapIndex), ('Mod5', X.Mod5MapIndex)]
        #This gets the list of all keycodes per Modifier, assigns to name
        for name, index in mod_index:
            codes = [v for v in list(modifier_mapping[index]) if v]
            mod_keycodes[name] = codes
            all_mod_keycodes += codes

        #Need to find out which Mod# to use for Alt, Num_Lock, and Super
        def lookup_keycode(string):
            keysym = self.string_to_keysym[string]
            return self.display.keysym_to_keycode(keysym)

        #List the keycodes for the named modifiers
        alt_keycodes = [lookup_keycode(i) for i in ['Alt_L', 'Alt_R']]
        num_lock_keycodes = [lookup_keycode('Num_Lock')]
        super_keycodes = [lookup_keycode(i) for i in ['Super_L', 'Super_R']]

        #Need to set aliases in both mod_keycodes and self.modifier_bits
        for name, keycodes in mod_keycodes.items():
            for alt_key in alt_keycodes:
                if alt_key in keycodes:
                    mod_keycodes['Alt'] = keycodes
                    self.modifier_bits['Alt'] = self.modifier_bits[name]
            for num_lock_key in num_lock_keycodes:
                if num_lock_key in keycodes:
                    mod_keycodes['Num_Lock'] = keycodes
                    self.modifier_bits['Num_Lock'] = self.modifier_bits[name]
            for super_key in super_keycodes:
                if super_key in keycodes:
                    mod_keycodes['Super'] = keycodes
                    self.modifier_bits['Super'] = self.modifier_bits[name]

        #Assign the mod_keycodes to a local variable for access
        self.modifier_keycodes = mod_keycodes

        self.all_mod_keycodes = all_mod_keycodes

    def lookup_character_keycode(self, character):
        """
        Looks up the keysym for the character then returns the keycode mapping
        for that keysym.
        """
        keysym = self.string_to_keysym.get(character, 0)
        if keysym == 0:
            keysym = self.string_to_keysym.get(special_X_keysyms[character], 0)
        return self.display.keysym_to_keycode(keysym)

    def get_translation_dicts(self):
        """
        Returns dictionaries for the translation of keysyms to strings and from
        strings to keysyms.
        """
        keysym_to_string_dict = {}
        string_to_keysym_dict = {}
        #XK loads latin1 and miscellany on its own; load latin2-4 and greek
        Xlib.XK.load_keysym_group('latin2')
        Xlib.XK.load_keysym_group('latin3')
        Xlib.XK.load_keysym_group('latin4')
        Xlib.XK.load_keysym_group('greek')

        #Make a standard dict and the inverted dict
        for string, keysym in Xlib.XK.__dict__.items():
            if string.startswith('XK_'):
                string_to_keysym_dict[string[3:]] = keysym
                keysym_to_string_dict[keysym] = string[3:]
        return keysym_to_string_dict, string_to_keysym_dict

    def ascii_printable(self, keysym):
        """Returns False if the keysym is not a printable ascii character."""
        #Why do I have to write this, there should be a good built-in...
        if 0 <= keysym < 9:
            return False
        elif keysym == 11 or keysym == 12:
            return False
        elif 13 < keysym < 32:
            return False
        elif keysym > 126:
            return False
        else:
            return True
