# UltraSystray #

Sane and simple cross-platform Python systray icon

Features
--------

* No external dependencies, tiny
* No temporary images or files on disk
* One Python file and one straight forward class per backend
* No threads or processes are started
* Icons have to be in ICO format on the filesystem (ICO is supported by all platforms)
* Supports the backends Win32, ~Darwin~, GTK StatusIcon, AppIndicator, ~QT5~

Icon Format
-----------

For all platforms, the recommended format to use is ICO.

Yes, you heard right, do neither use SVG nor PNG because it will not work on all platforms.

ICO is a Microsoft container format that can contain multiple icons in different sizes. This is ideal because the OS
can pick just the right size and doesn't need to scale.

Advantages of ICO:
 * contains the same icon in different sizes
 * full control over the rendering of the icons
 * no dependency or quality limitations on platform specific SVG renderers
 * fast because nothing has to be scaled on runtime
 * works on all platforms, including Linux/GTK

AppIndicator Warning
--------------------

(AppIndicators)[https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators] were invented by Ubuntu to
create more consistency in your system tray.

They tried to achieve this by removing a lot of basic, major functionality like the ability to do something on a
left mouse button click. Yes, you heard right, AppIndicators make it impossible to have any action on a left click.
On the other hand, you can do something on double-left-click or on middle-click.

This is obviously a rather eratic decision that does not fit with modern UI design requirements like consistency and expectability.
Nobody will expect that left clicks don't work but double clicks might do something now. I can already imagine people wildly double
clicking all their tray icons in the hopes that might do something.

This restriction alone is so huge that AppIndicators are doomed to die sooner or later.

Thus, the strong recommendation is *not to use AppIndicators*. This is not a sustainable standard for the future.

What should be used instead? Use classical status icons. They are officially being removed from GTK>4, so there will be in the future
an additional library on top of GTK for status icons, ie. (XApp.StatusIcon)[https://lazka.github.io/pgi-docs/XApp-1.0/classes/StatusIcon.html]
It is expected that this library will automatically be available on all major Linux desktops.

