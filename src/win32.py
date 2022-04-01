# coding=utf-8
# pystray
# Copyright (C) 2016-2022 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import ctypes
import threading

from ctypes import wintypes

from . import win32_adapter as win32

class SystrayIcon():
    _HWND_TO_ICON = {}

    def __init__(self, unique_id=None, icon=None, tooltip=None, menu_items=None, **kwargs):

        
        # unique_id not used in this implementation
        self.unique_id = unique_id

        self.visible = True
        self.icon = icon
        self.tooltip = tooltip
        self.menu_items = menu_items
        self.menu = None

        self._icon_handle = None
        self._hwnd = None
        self._menu_hwnd = None
        self._menu_handle = None
        self._hmenu = None
        self._running = False

    def __del__(self):
        if self._running:
            self.quit()
            #if self._thread.ident != threading.current_thread().ident:
            #    self._thread.join()
        #self._release_icon()

    def _show(self):
        self._assert_icon_handle()
        self._message(
            win32.NIM_ADD,
            win32.NIF_MESSAGE | win32.NIF_ICON | win32.NIF_TIP,
            uCallbackMessage=win32.WM_NOTIFY,
            hIcon=self._icon_handle,
            szTip=self.tooltip)

    def _hide(self):
        self._message(win32.NIM_DELETE, 0)

    def _update_icon(self):
        self._release_icon()
        self._assert_icon_handle()
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_ICON,
            hIcon=self._icon_handle)
        self._icon_valid = True

    def _update_title(self):
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_TIP,
            szTip=self.tooltip)

    def _notify(self, message, title=None):
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_INFO,
            szInfo=message,
            szInfoTitle=title or self.tooltip or '')

    def _remove_notification(self):
        self._message(
            win32.NIM_MODIFY,
            win32.NIF_INFO,
            szInfo='')

    def destroy_menu(self):
        try:
            hmenu, callbacks = self._menu_handle
            win32.DestroyMenu(hmenu)
        except:
            pass

    def _update_menu(self):
        self.destroy_menu()

        callbacks = []
        hmenu = self.create_menu(self.menu_items)
        self.menu = hmenu
        print('update menu', hmenu)
        if hmenu:
            self._menu_handle = (hmenu, callbacks)
        else:
            self._menu_handle = None

    def run(self):

        @win32.TypeConsoleCtrlHandler
        def console_handler(ctrl_type):
            if ctrl_type == win32.CTRL_C_EVENT:
                self.quit()
            return False

        if not win32.SetConsoleCtrlHandler(console_handler, True):
            raise RuntimeError('SetConsoleCtrlHandler failed.')

        self._atom = self._register_class()

        # This is a mapping from win32 event codes to handlers used by the
        # mainloop
        self._message_handlers = {
            win32.WM_STOP: self.quit,
            win32.WM_NOTIFY: self._on_notify,
            win32.WM_TASKBARCREATED: self._on_taskbarcreated
        }

        # Create the message loop
        msg = wintypes.MSG()
        lpmsg = ctypes.byref(msg)
        win32.PeekMessage(
            lpmsg, None, win32.WM_USER, win32.WM_USER, win32.PM_NOREMOVE)

        self._hwnd = self._create_window(self._atom)
        self._menu_hwnd = self._create_window(self._atom)
        self._HWND_TO_ICON[self._hwnd] = self

        #self._mark_ready()

        # Run the event loop
        #self._thread = threading.current_thread()

        self._update_menu()

        self._show()

        self._mainloop()

    def _run_detached(self):
        threading.Thread(target=lambda: self._run()).start()

    def _stop(self):
        win32.PostMessage(self._hwnd, win32.WM_STOP, 0, 0)

    def _mainloop(self):
        """The body of the main loop thread.

        This method retrieves all events from *Windows* and makes sure to
        dispatch clicks.
        """
        # Pump messages
        try:
            msg = wintypes.MSG()
            lpmsg = ctypes.byref(msg)
            while True:
                r = win32.GetMessage(lpmsg, None, 0, 0)
                if not r:
                    break
                elif r == -1:
                    break
                else:
                    win32.TranslateMessage(lpmsg)
                    win32.DispatchMessage(lpmsg)

        except Exception as e:
            print('An error occurred in the main loop')
            raise e

        finally:
            try:
                self._hide()
                del self._HWND_TO_ICON[self._hwnd]
            except:
                # Ignore
                pass

            #win32.DestroyWindow(self._hwnd)
            #win32.DestroyWindow(self._menu_hwnd)
            #if self._menu_handle:
            #    hmenu, callbacks = self._menu_handle
            #    win32.DestroyMenu(hmenu)
            #self._unregister_class(self._atom)

    @classmethod
    def quit(cls, wparam=0, lparam=0):
        """Handles ``WM_STOP``.

        This method posts a quit message, causing the mainloop thread to
        terminate.
        """
        win32.PostQuitMessage(0)

    def on_left_click(self, *args):
        print('left click')

    def on_middle_click(self, *args):
        print('middle click')
        self.quit()

    def on_right_click(self, *args):
        print('right click', args)
        # TrackPopupMenuEx does not behave unless our systray window is the
        # foreground window
        win32.SetForegroundWindow(self._hwnd)

        # Get the cursor position to determine where to display the menu
        point = wintypes.POINT()
        win32.GetCursorPos(ctypes.byref(point))

        # Display the menu and get the menu item identifier; the identifier
        # is the menu item index
        hmenu, descriptors = self._menu_handle
        index = win32.TrackPopupMenuEx(
            self.menu,
            win32.TPM_RIGHTALIGN | win32.TPM_BOTTOMALIGN
            | win32.TPM_RETURNCMD,
            point.x,
            point.y,
            self._menu_hwnd,
            None)
        if index > 0:
            self.menu_items[index]['callback'](index)

        win32.PostMessage(self._hwnd, 0, 0, 0)

    def _on_notify(self, wparam, lparam):
        """Handles ``WM_NOTIFY``.

        If this is a left button click, this icon will be activated. If a menu
        is registered and this is a right button click, the popup menu will be
        displayed.
        """

        if lparam == win32.WM_LBUTTONUP:
            self.on_left_click()

        if lparam == win32.WM_MBUTTONUP:
            self.on_middle_click()

        elif lparam == win32.WM_RBUTTONUP:
            self.on_right_click(wparam, lparam)

    def _on_taskbarcreated(self, wparam, lparam):
        """Handles ``WM_TASKBARCREATED``.

        This message is broadcast when the notification area becomes available.
        Handling this message allows catching explorer restarts.
        """
        if self.visible:
            self._show()

    def _create_window(self, atom):
        """Creates the system tray icon window.

        :param atom: The window class atom.

        :return: a window
        """
        # Broadcast messages (including WM_TASKBARCREATED) can be caught
        # only by top-level windows, so we cannot create a message-only window
        hwnd = win32.CreateWindowEx(
            0,
            atom,
            None,
            win32.WS_POPUP,
            0, 0, 0, 0,
            0,
            None,
            win32.GetModuleHandle(None),
            None)

        # On Vista+, we must explicitly opt-in to receive WM_TASKBARCREATED
        # when running with escalated privileges
        win32.ChangeWindowMessageFilterEx(
            hwnd, win32.WM_TASKBARCREATED, win32.MSGFLT_ALLOW, None)
        return hwnd

    def create_menu(self, items=None):
        """Creates a :class:`ctypes.wintypes.HMENU` from a
        :class:`pystray.Menu` instance.

        :param descriptors: The menu descriptors. If this is falsy, ``None`` is
            returned.

        :param callbacks: A list to which a callback is appended for every menu
            item created. The menu item IDs correspond to the items in this
            list plus one.

        :return: a menu
        """
        # Generate the menu
        hmenu = win32.CreatePopupMenu()
        i = 0
        if items:
            for item in items:
                menu_item = self.create_menu_item(index=i, **item)
                win32.InsertMenuItem(hmenu, i, True, ctypes.byref(menu_item))
                i += 1

        menu_info = win32.MENUINFO(
            cbSize=ctypes.sizeof(win32.MENUINFO),
            fMask=win32.MIM_STYLE,
            dwStyle=win32.MNS_AUTODISMISS | win32.MNS_CHECKORBMP,
        )

        #win32.SetMenuInfo(hmenu, ctypes.byref(menu_info))
        return hmenu

    def create_menu_item(self, index, label='', callback=None, variant='default', active=True, enabled=True):

        """Creates a :class:`pystray._util.win32.MENUITEMINFO` from a
        :class:`pystray.MenuItem` instance.

        :param descriptor: The menu item descriptor.

        :param callbacks: A list to which a callback is appended for every menu
            item created. The menu item IDs correspond to the items in this
            list plus one.

        :return: a :class:`pystray._util.win32.MENUITEMINFO`
        """
        default = False
        checked = False
        if variant == 'separator':
            return win32.MENUITEMINFO(
                cbSize=ctypes.sizeof(win32.MENUITEMINFO),
                fMask=win32.MIIM_FTYPE,
                fType=win32.MFT_SEPARATOR)
        else:
            return win32.MENUITEMINFO(
                cbSize=ctypes.sizeof(win32.MENUITEMINFO),
                fMask=win32.MIIM_ID | win32.MIIM_STRING | win32.MIIM_STATE | 
                    win32.MIIM_FTYPE | win32.MIIM_SUBMENU,
                wID=index,
                dwTypeData=label,
                fState=0 | 
                    (win32.MFS_DEFAULT if default else 0) | 
                    (win32.MFS_CHECKED if checked else 0) | 
                    (win32.MFS_DISABLED if not active else 0),
                fType=win32.MFT_STRING | 
                    (win32.MFT_RADIOCHECK if variant == 'radio' else 0),
                hSubMenu=None
                #hSubMenu=self.create_menu(descriptor.submenu, callbacks)
                #if descriptor.submenu
                #else None
                )

    def _message(self, code, flags, **kwargs):
        """Sends a message the the systray icon.

        This method adds ``cbSize``, ``hWnd``, ``hId`` and ``uFlags`` to the
        message data.

        :param int message: The message to send. This should be one of the
            ``NIM_*`` constants.

        :param int flags: The value of ``NOTIFYICONDATAW::uFlags``.

        :param kwargs: Data for the :class:`NOTIFYICONDATAW` object.
        """
        win32.Shell_NotifyIcon(code, win32.NOTIFYICONDATAW(
            cbSize=ctypes.sizeof(win32.NOTIFYICONDATAW),
            hWnd=self._hwnd,
            hID=id(self),
            uFlags=flags,
            **kwargs))

    def _release_icon(self):
        """Releases the icon handle and sets it to ``None``.

        If not icon handle is set, no action is performed.
        """
        if self._icon_handle:
            win32.DestroyIcon(self._icon_handle)
            self._icon_handle = None

    def _assert_icon_handle(self):
        """Asserts that the cached icon handle exists.
        """
        if self._icon_handle:
            return

        print("load", str(self.icon), self._icon_handle)

        #with serialized_image(self.icon, 'ICO') as icon_path:
        try:
            self._icon_handle = win32.LoadImage(
                None,
                str(self.icon),
                win32.IMAGE_ICON,
                0,
                0,
                win32.LR_DEFAULTSIZE | win32.LR_LOADFROMFILE)
        except:
            self._icon_handle = win32.LoadImage(
                None,
                str(self.icon),
                win32.IMAGE_ICON,
                0,
                0,
                win32.LR_DEFAULTSIZE | win32.LR_LOADFROMFILE)


    def _register_class(self):
        """Registers the systray window class.

        :return: the class atom
        """
        return win32.RegisterClassEx(win32.WNDCLASSEX(
            cbSize=ctypes.sizeof(win32.WNDCLASSEX),
            style=0,
            lpfnWndProc=_dispatcher,
            cbClsExtra=0,
            cbWndExtra=0,
            hInstance=win32.GetModuleHandle(None),
            hIcon=None,
            hCursor=None,
            hbrBackground=win32.COLOR_WINDOW + 1,
            lpszMenuName=None,
            lpszClassName='%s%dSystemTrayIcon' % (self.tooltip, id(self)),
            hIconSm=None))

    def _unregister_class(self, atom):
        """Unregisters the systray window class.

        :param atom: The class atom returned by :meth:`_register_class`.
        """
        win32.UnregisterClass(atom, win32.GetModuleHandle(None))


@win32.TypeMessageHandler
def _dispatcher(hwnd, uMsg, wParam, lParam):
    """The function used as window procedure for the systray window.
    """

    #print('dispatcher', uMsg, wParam, lParam)

    # These messages are sent before Icon._HWND_TO_ICON[hwnd] has been set, so
    # we handle them explicitly
    if uMsg == win32.WM_NCCREATE:
        return True
    if uMsg == win32.WM_CREATE:
        return 0

    try:
        icon = SystrayIcon._HWND_TO_ICON[hwnd]
    except KeyError:
        return win32.DefWindowProc(hwnd, uMsg, wParam, lParam)

    try:
        return int(icon._message_handlers.get(
            uMsg, lambda w, l: 0)(wParam, lParam) or 0)

    except Exception as e:
        print('An error occurred when calling message handler')
        raise e