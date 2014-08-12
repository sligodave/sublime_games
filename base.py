
import uuid as u
import math
import os.path

import sublime


class Game(object):
    def __init__(self, view=None, settings=None, configure=True):
        if view is None:
            window = sublime.active_window()
            view = window.new_file()
        self.view = view
        self.colors = []
        self.settings = {
            'font_face': 'Courier New',
            'font_size': 20,
            'line_numbers': False,
            'gutter': False,
            'margin': 0,
            'rulers': [],
            'caret_style': 'solid',
            'spell_check': False,
            'word_wrap': False,
            'draw_centered': True,
            'line_padding_top': 0,
            'line_padding_bottom': 0,
            'highlight_line': False,
            'draw_white_space': 'none',
            'scroll_past_end': False,
            'draw_indent_guides': False,
            'show_line_endings': False,
            'name': 'Game',
            'scratch': True,
            'read_only': True,
        }
        if settings is not None:
            self.settings.update(settings)
        if configure:
            self.configure_view()

    def configure_view(self, **kwargs):
        for name, value in self.settings.items():
            if name not in kwargs:
                kwargs[name] = value
        self.clear_selection()
        if 'scratch' in kwargs:
            self.view.set_scratch(kwargs.pop('scratch'))
        if 'read_only' in kwargs:
            self.view.set_read_only(kwargs.pop('read_only'))
        if 'name' in kwargs:
            self.view.set_name(kwargs.pop('name'))
        settings = self.view.settings()
        for name, value in kwargs.items():
            settings.set(name, value)

    def zoom(self, amount, clear=False):
        self.view.settings().set('font_size', self.view.settings().get('font_size') + amount)
        if clear:
            self.clear_selection()

    def clear_selection(self):
        sel = self.view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))

    def generate_colors_xml(self, colors=None):
        if colors is None:
            colors = self.colors
        colors_xml = ''
        if isinstance(colors, list):
            defaults = {
                'name': '', 'scope': '', 'caret': '',
                'background': '', 'foreground': '', 'fontStyle': ''
            }
            color_xml = '''<dict><key>name</key><string>{name}</string><key>scope</key>
<string>{scope}</string><key>settings</key><dict><key>background</key><string>{background}</string>
<key>foreground</key><string>{foreground}</string><key>caret</key><string>{caret}</string>
<key>fontStyle</key><string>{fontStyle}</string></dict></dict>'''
            colors_xml = ''.join(
                [
                    color_xml.format(
                        **dict(list(defaults.items()) + list(x.items()))
                    )
                    for x in colors
                ]
            )
        else:
            colors_xml = str(colors)
        return colors_xml

    def generate_theme_xml(
        self,
        colors=None,
        background='#ffffff',
        foreground='#000000',
        caret='#ffffff',
        fontStyle='bold',
        uuid=None
    ):
        if uuid is None:
            uuid = u.uuid4()
        colors_xml = self.generate_colors_xml(colors)
        return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plistPUBLIC
'-//Apple Computer//DTD PLIST 1.0//EN''http://www.apple.com/DTDs/PropertyList-1.0.dtd'>
<plist version="1.0"><dict><key>name</key><string>Color Scheme</string><key>settings</key><array>
<dict><key>settings</key><dict><key>background</key><string>{background}</string><key>caret</key>
<string>{caret}</string><key>foreground</key><string>{foreground}</string><key>fontStyle</key>
<string>{fontStyle}</string></dict></dict>{colors}</array><key>uuid</key>
<string>{uuid}</string></dict></plist>'''.format(
            uuid=uuid, colors=colors_xml, background=background,
            foreground=foreground, caret=caret, fontStyle=fontStyle
        )

    def set_color_scheme(
        self,
        xml=None,
        filename=None,
        colors=None,
        background='#ffffff',
        foreground='#000000',
        caret='#ffffff',
        fontStyle='bold',
        uuid=None
    ):
        if xml is None:
            xml = self.generate_theme_xml(colors, background, foreground, caret, fontStyle, uuid)
        if filename is None:
            filename = '%s.tmTheme' % (self.__class__.__name__)
        packages_path = sublime.packages_path()
        with open(os.path.join(packages_path, 'User', filename), 'w') as theme_file:
            theme_file.write(xml)
        settings = self.view.settings()
        settings.set('color_scheme', 'Packages/User/%s' % filename)

    def centered_text(self, text, width):
        left = ' ' * (int(math.floor((width - len(text)) / 2)))
        right = ' ' * (width - len(text) - len(left))
        return '%s%s%s' % (left, text, right)
