
import sublime
import sublime_plugin

class UtilsEditViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, data=None, start=0, end=None):
        start = int(start)
        if end is not None:
            end = int(end)
        was_read_only = self.view.is_read_only()
        if was_read_only:
            self.view.set_read_only(False)
        if end is not None and not start == end:
            if data is not None:
                self.view.replace(edit, sublime.Region(start, end), data)
            else:
                self.view.erase(edit, sublime.Region(start, end))
        elif data is not None:
            self.view.insert(edit, start, data)
        if was_read_only:
            self.view.set_read_only(True)
