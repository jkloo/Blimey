import os
import re

import sublime
import sublime_plugin


class SphinxTemplateCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        """
        read in the current line
        if not: line matches 'def <func-name>([<param> ... ])'
            return
        else:
            check the next line for \"\"\"
            if: match flag EXISTING_DOCSTING

        for each param:
            strip defaults
            strip 'self'
            wrap in sphinx-style markup

        writeout spinx comments using EXISTING_DOCSTING to determine line.

        """
        FUNC_P = r'^\s*def[ ]+[\w_]+\(\s*((?:[*\w_]+,\s*)*[*\w_]+)\):'
        selections = list(self.view.sel())
        selections.reverse()

        for sel in selections:
            line = self.view.line(sel)
            text = self.view.substr(line)


        print(self.view.line())


    # def is_enabled(self):
        # settings = sublime.load_settings('Blimey.sublime-settings')
        # return settings.get('sphinx-template', False) and os.path.splitext(self.view.file_name())[-1].strip('.') in ['py']
