# UltraSystray
#
# Copyright (C) 2022 Ronny Rentner
#

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
gi.require_version("GdkX11", "3.0")

from gi.repository import Gtk, GLib, GObject
from gi.repository import AyatanaAppIndicator3 as AppIndicator
from gi.repository import Notify

import pathlib
import signal

class Icon():
    def __init__(self, unique_id=None, icon=None, title=None, menu_items=None, **kwargs):
        self.appindicator = None

        self.unique_id = unique_id or self.generate_random_id()
        self.icon = icon
        self.title = title
        self.menu_items = menu_items

    def generate_random_id(self):
        # Generate random id if none was provided
        import random, string
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))

    def show(self):

        if isinstance(self.icon, pathlib.Path):
            self.appindicator = AppIndicator.Indicator.new_with_path(
                self.unique_id,
                self.icon.stem,
                AppIndicator.IndicatorCategory.APPLICATION_STATUS,
                str(self.icon.parent))
        else:
            self.appindicator = AppIndicator.Indicator.new(
                self.unique_id,
                self.icon,
                AppIndicator.IndicatorCategory.APPLICATION_STATUS)

        self.appindicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        # Appindicators must have a menu attached or otherwise they are not visible
        self.set_menu(self.create_menu(items=self.menu_items))

        # Middle click executes last menu item (which should be quit)
        self.set_middle_click_target(item=-1)

        if self.title:
            self.appindicator.set_title(self.title)
            GLib.set_application_name(self.title)

        Notify.init(self.unique_id)

    def abouttoshow(self, *args):
        print("abouttoshow", *args)

    def event(self, *args):
        print("event", *args)

    def run(self):
        # Make sure that we do not inhibit CTRL-C;
        # this is only possible from the main thread
        try: signal.signal(signal.SIGINT, signal.SIG_DFL)
        except ValueError: pass

        self.show()

        server = GObject.GObject.get_property(self.appindicator, "dbus-menu-server")
        print('server', server)
        root = GObject.GObject.get_property(server, "root-node")
        print('root', root)
        root.connect('about-to-show', self.abouttoshow)
        root.connect('event', self.event)
        root.connect('item-activated', self.event)
        server.connect('item-activation-requested', self.event)

        Gtk.main()

    def set_middle_click_target(self, item=-1):
        menu = self.appindicator.get_menu()
        children = menu.get_children()
        self.appindicator.set_secondary_activate_target(children[item])

    def set_title(self, title):
        self.title = title
        self.appindicator.set_title(self.title)

    def set_menu(self, menu):
        # Appindicators must have a menu attached or otherwise they are not visible
        self.appindicator.set_menu(menu)

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

    @classmethod
    def quit(cls, menu_item):
        Gtk.main_quit()
