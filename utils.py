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
