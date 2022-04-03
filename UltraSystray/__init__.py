def SystrayIcon(*args, **kwargs):
    import sys
    if sys.platform.startswith('win32'):
        from .win32 import SystrayIcon
    elif sys.platform.startswith('darwin'):
        from .darwin import SystrayIcon
    else:
        from .gtk import SystrayIcon

    return SystrayIcon(*args, **kwargs) 
