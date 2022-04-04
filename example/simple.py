import pathlib, sys, time, threading

# Make the example find UltraSystray relative to itself
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from UltraSystray import SystrayIcon, DefaultIcons

icons = pathlib.Path(__file__).parent.parent / 'icons'
assert icons.exists()

icon_file = icons / 'arrow.ico'
assert icon_file.exists()

def do_something(menu_item):
    print("Doing something for 5 seconds...")
    print("This will block the UI!")
    time.sleep(5)
    print("Done...")

def update_menu():
    pass

def run_thread():
    # In order for the icon to be displayed, you must provide an icon
    tray = SystrayIcon(icon=icon_file, tooltip='Systray demo')
    tray.menu_items = [
        { 'label': 'Choice 1', 'variant': 'radio', 'callback': do_something },
        { 'label': 'Choice 2', 'variant': 'radio', 'callback': do_something },
        { 'label': 'Choice 3', 'variant': 'radio', 'callback': do_something },
        { 'variant': 'separator' },
        { 'label': 'Another entry', 'callback': do_something },
        { 'label': 'Do something', 'callback': do_something },
        { 'variant': 'separator' },
        { 'label': 'Quit', 'callback': tray.quit }
    ]

    # Create system tray window and show it
    tray.run()

thread = threading.Thread(target=run_thread)
thread.start()

print("Tray started")

print("Doing something else for 5 seconds")
time.sleep(5)
print("Done")
