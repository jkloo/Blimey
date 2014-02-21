import os
import re
import sublime_plugin
import sublime
import json

CPP = 'cpp'
H = 'h'
C = 'c'


class ConvertMisraCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command('convert_misra_types')
        self.view.run_command('convert_misra_pnd_defs')
        self.view.run_command('convert_misra_protect_pnd_defs')


class ConvertMisraTypesCommand(sublime_plugin.TextCommand):
    # List of tuples because order matters, and ST2 uses py2.6 which does not
    # have OrderedDict built-in
    MISRA_TYPES = [('char', 'CHAR'),
                   ('boolean', 'BOOLEAN'),
                   ('bool', 'BOOL'),
                   ('unsigned short', 'UINT16'),
                   ('short', 'INT16'),
                   ('unsigned int', 'UINT32'),
                   ('int', 'INT32'),
                   ('unsigned long long', 'UINT64'),
                   ('long long', 'INT64'),
                   ('float', 'FLOAT4'),
                   ('double', 'FLOAT8'),
                   ('true', 'TRUE'),
                   ('false', 'FALSE')]

    def run(self, edit):
        for t in self.MISRA_TYPES:
            regions = self.view.find_all('(?:\W){0}(?:\W)'.format(t[0]))
            regions.reverse()
            for r in regions:
                self.view.replace(edit, r, self.view.substr(r.begin()) + t[1] + self.view.substr(r.end() - 1))

    def is_enabled(self):
        return (self.view.file_name() and (len(self.view.file_name()) > 0)
                and (os.path.splitext(self.view.file_name())[1][1:] in (C, H, CPP)))


class ConvertMisraPndDefsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        FILE_PATH = self.view.file_name()
        FILE_TYPE = os.path.splitext(FILE_PATH)[1][1:]
        PNDDEF_P = r'#define\s+([A-Z_0-9]+)\s+(\(?[\-0-9A-Fa-fxU]+\)?(?:\s+(?:<<|>>)\s+[\-0-9A-Fa-fxU]+\))?)'
        PNDDEF_REPL_P = '#ifdef __cplusplus\n    const INT32 {0} = {1};\n#else\n    #define {0} {1}\n#endif'
        if FILE_TYPE in (CPP,):
            PNDDEF_REPL_P = 'const INT32 {0} = {1};'
        regions = self.view.find_all(PNDDEF_P)
        regions.reverse()
        for r in regions:
            text = self.view.substr(r)
            m = re.search(PNDDEF_P, text)
            if m:
                self.view.replace(edit, r, PNDDEF_REPL_P.format(m.group(1), m.group(2)))

    def is_enabled(self):
        return (self.view.file_name() and (len(self.view.file_name()) > 0)
                and (os.path.splitext(self.view.file_name())[1][1:] in (C, H, CPP)))


# convert __[A-Z_0-9]__H style #defines to [A-Z_0-9]__H in *.h
class ConvertMisraProtectPndDefsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        PNDDEF_P = r'#ifn?def\s+(__[a-zA-Z_0-9]+__H)'
        h = self.view.find(PNDDEF_P, 0)
        if h:  # matched the protective #ifdef
            s = self.view.substr(h)
            m = re.search(PNDDEF_P, s)  # need to extract the name, so match again
            if m:
                h_ = m.group(1)  # e.g. __THE_THING__H
                regions = self.view.find_all(h_)  # find all instances of __THE_THING__H
                if regions:
                    regions.reverse()
                    for r in regions:
                        # trim off the leading '__'
                        self.view.replace(edit, r, h_[2:])

    def is_enabled(self):
        return (self.view.file_name() and (len(self.view.file_name()) > 0)
                and (os.path.splitext(self.view.file_name())[1][1:] in (H,)))
