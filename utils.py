import os
import re

import sublime
import sublime_plugin


class SplitOnCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        selections = list(self.view.sel())
        selections.reverse()
        split_char = kwargs.get('split_char', '')
        if split_char:
            le = '\n'
            for selection in selections:
                current_line = self.view.line(selection)
                padding = ' ' * (selection.begin() - current_line.begin())
                text = self.view.substr(selection)
                elements = [x.strip() for x in text.split(split_char)]
                elements[1:] = [padding + x for x in elements[1:]]
                new_text = (split_char + le).join(elements)
                self.view.replace(edit, selection, new_text)


HEADING_P = r'^(#+)[ \t]*[\d\.]*[ \t]*(.*)$'

class Heading(object):
    def __init__(self, line):
        m = re.match(HEADING_P, line)
        self.level = len(m.group(1))
        self.text = m.group(2)
        if self.level == 1:
            self.format = "{0}.0"
        else:
            self.format = '.'.join(['{{{v}}}'.format(v=i) for i in range(self.level)])
        self.value = ''

    def format_value(self, levels):
        if self.level > len(levels):
            levels.append(1)
        elif self.level == len(levels):
            levels[-1] += 1
        else:
            levels[self.level - 1] += 1
            levels[self.level: ] = [0] * len(levels[self.level: ])
        self.value = self.format.format(*levels[:self.level])
        return levels

    def __str__(self):
        return ' '.join(['#' * self.level, self.value, self.text])


class MarkdownHeadings(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        regions = self.view.find_all(HEADING_P)
        headings = []
        levels = [0]
        for r in regions:
            h = Heading(self.view.substr(r))
            levels = h.format_value(levels)
            headings.append(h)            
        headings.reverse()
        regions.reverse()
        for i in range(len(regions)):
            self.view.replace(edit, regions[i], str(headings[i]))

    def is_enabled(self):
        settings = sublime.load_settings('Blimey.sublime-settings')
        return settings.get('md-heading-numbers', False) and os.path.splitext(self.view.file_name())[-1].strip('.') in ['md', 'markdown']


class MarkdownHeadingsListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command('markdown_headings')
