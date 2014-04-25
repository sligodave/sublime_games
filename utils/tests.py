
import os
import os.path

import sublime
import sublime_plugin

from .commands import UtilsEditViewCommand
from .touch import (
    add_event_handler,
    add_event_handler_async,
    add_event_handlers,
    add_event_handlers_async,
    remove_event_handler,
    remove_event_handler_async,
    remove_event_handlers,
    remove_event_handlers_async,
    LiveEventListener,
    TOUCH_EVENT_HANDLERS
)


tmTheme_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>name</key><string>Color Schemes Theme</string><key>settings</key>
<array><dict><key>settings</key><dict><key>background</key><string>#ffffff</string><key>caret</key>
<string>#000000</string><key>foreground</key><string>#000000</string><key>fontStyle</key>
<string>bold</string></dict></dict><dict><key>name</key><string>orange</string><key>scope</key>
<string>orange</string><key>settings</key><dict><key>background</key><string>#ff7f00</string>
<key>foreground</key><string>#000000</string><key>caret</key><string>#ff7f00</string></dict></dict>
<dict><key>name</key><string>yellow</string><key>scope</key><string>yellow</string>
<key>settings</key><dict><key>background</key><string>#ffec38</string><key>foreground</key>
<string>#000000</string><key>caret</key><string>#ffec38</string></dict></dict><dict><key>name</key>
<string>red</string><key>scope</key><string>red</string><key>settings</key><dict>
<key>background</key><string>#ff3a2f</string><key>foreground</key><string>#000000</string>
<key>caret</key><string>#ff3a2f</string></dict></dict></array><key>uuid</key>
<string>90533C5A-2E43-938F-2C9C-A338EEFDED3F</string></dict></plist>"""


class UtilsTouchTestCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        self.view = view = window.new_file()
        view.set_scratch(True)

        base_path = sublime.packages_path()
        theme_path = 'Packages/User/touch_test_%d.tmTheme' % view.id()
        theme_full_path = os.path.join(os.path.split(base_path)[0], theme_path)
        with open(theme_full_path, 'w') as theme_open:
            theme_open.write(tmTheme_xml)
        settings = view.settings()
        settings.set('color_scheme', theme_path)
        settings.set('UTILS_TEST_VIEW_THEME_PATH', theme_full_path)

        data = '-----XXXXX-----'
        view.run_command('utils_edit_view', {'data': data, 'start': 0, 'end': view.size()})
        region = sublime.Region(5, 10)
        self.handler_id = add_event_handler(view, region, self.handler_click1)
        sel = view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))

    def handler_click1(self, handler_id, view, region, point):
        print(handler_id)
        print(view)
        print(region)
        print(point)
        remove_event_handler(view, self.handler_id)


class UtilsTouchTestEventListener(sublime_plugin.EventListener):
    def on_close(self, view):
        theme_full_path = view.settings().get('UTILS_TEST_VIEW_THEME_PATH')
        if theme_full_path is not None and os.path.exists(theme_full_path):
            print('Removing theme file "%s"' % theme_full_path)
            os.unlink(theme_full_path)
