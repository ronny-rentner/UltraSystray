# UltraSystray
#
# Copyright (C) 2022 Ronny Rentner
#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import pathlib
import signal

class SystrayIcon():
    def __init__(self, unique_id=None, icon=None, tooltip=None, menu_items=None, **kwargs):

        # unique_id not used in this implementation
        self.unique_id = unique_id

        self.icon = icon
        self.tooltip = tooltip
        self.menu_items = menu_items
        self.menu = None

    def show(self): 
        if self.menu_items:
            self.set_menu(self.create_menu(items=self.menu_items))

        self.status_icon = Gtk.StatusIcon.new()
        self.status_icon.connect('activate', self.on_left_click)
        self.status_icon.connect('button-release-event', self.on_click)
        self.status_icon.connect('popup-menu', self.on_right_click)

        if isinstance(self.icon, pathlib.Path):
            self.status_icon.set_from_file(str(self.icon))
        else:
            self.status_icon.set_from_stock(self.icon)

        self.set_tooltip(self.tooltip)
        
    def run(self):
        # Make sure that we do not inhibit CTRL-C;
        # this is only possible from the main thread
        try: signal.signal(signal.SIGINT, signal.SIG_DFL)
        except ValueError: pass

        self.show()
        Gtk.main()

    def on_click(self, status_icon=None, event_button=None, *args):
        if event_button and event_button.button == 2:
            self.on_middle_click()

    def on_left_click(self, *args):
        print('left click', args)

    def on_middle_click(self, *args):
        print('middle click', args)

    def on_right_click(self, *args):
        print('right click', args)
        if self.menu:
            self.menu.popup(None, None, self.status_icon.position_menu, self.status_icon, args[1], args[2]);

    def set_tooltip(self, tooltip):
        self.tooltip = tooltip
        self.title = tooltip 

        if not self.tooltip:
            return

        self.status_icon.set_tooltip_text(self.tooltip)
        # We use the tooltip also as title at the same time
        self.status_icon.set_title(self.title)

    def set_menu(self, menu):
        self.menu = menu

    def create_menu(self, items=None):
        menu = Gtk.Menu.new()
        if items:
            for item in items:
                menu.append(self.create_menu_item(**item))
        else:
            menu.append(self.create_menu_item('Quit', Gtk.main_quit))
        menu.show_all()

        return menu

    def create_menu_item(self, label='', callback=None, variant='default', active=True, enabled=True):

        if variant == 'separator':
            return Gtk.SeparatorMenuItem()

        menu_item = None
        if variant == 'check':
            menu_item = Gtk.CheckMenuItem.new_with_label(label)
            menu_item.set_active(active)
        else:
            menu_item = Gtk.MenuItem.new_with_label(label)
            menu_item.set_sensitive(enabled)

        menu_item.connect('activate', callback)

        return menu_item

    # For convenience
    quit = Gtk.main_quit
