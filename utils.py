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


class Heading(object):
    def __init__(self, line):
        P = r'^(#+)[ \t]*[\d\.]*[ \t]*(.*)$'
        m = re.match(P, line)
        self.level = len(m.group(1))
        self.text = m.group(2)
        if self.level == 1:
            self.format = "{0}.0"
        else:
            self.format = '.'.join(['{{{}}}'.format(i) for i in range(self.level)])
        self.value = ''

    def format_value(self, levels):
        print(self.format)
        print(levels)
        self.value = self.format.format(*levels)

    def __str__(self):
        return ' '.join(['#' * self.level, self.value, self.text])


class MarkdownHeadings(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        print('running')
        regions = self.view.find_all(r'^(#+)[ \t]*[\d\.]*[ \t]*(.*)$')
        headings = []
        print(len(regions))
        for r in regions:
            headings.append(Heading(self.view.substr(r)))
        levels = [0]
        for h in headings:
            if h.level > len(levels):
                levels.append(1)
            elif h.level == len(levels):
                levels[-1] += 1
            else:
                levels[h.level - 1] += 1
                levels[h.level: ] = [0] * len(levels[h.level: ])
            h.format_value(levels[:h.level])
        headings.reverse()
        regions.reverse()
        for i in range(len(regions)):
            self.view.replace(edit, regions[i], str(headings[i]))

    def is_enabled(self):
        return os.path.splitext(self.view.file_name())[-1].strip('.') in ['md', 'markdown']


class MarkdownHeadingsListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command('markdown_headings')
