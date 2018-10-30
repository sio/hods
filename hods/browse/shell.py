'''
Interactive shell for browsing HODS documents
'''


import re
import shlex
from cmd import Cmd
from collections import namedtuple, OrderedDict
from functools import lru_cache
from itertools import islice
from math import log10

from hods.browse.cache import DocumentsReadOnlyCache


PathItem = namedtuple('PathItem', 'step,is_leaf')


class DocumentBrowser(Cmd):
    intro = 'Interactive document browser for HODS (https://hods.ml)'
    prompt = '(hods) > '


    def __init__(self, cache_file, browse_directory, *a, **ka):
        '''Initialize document browser with a cache file'''
        super().__init__(*a, **ka)
        self.directory = browse_directory
        self.stack = [[]] # collection of paths (and-joined)
        self.cache = DocumentsReadOnlyCache(cache_file)
        self.do_recache()


    @property
    def path(self):
        '''Current path (sequence of PathItem tuples)'''
        return self.stack[-1]  # last one must be the newest, we rely on that in _list_items


    @property
    def path_items(self):
        '''Content of the current branch'''
        return self.get_pathitems()


    def get_pathitems(self, field=None):
        '''Content of the current branch'''
        paths_hashable = tuple(tuple(p) for p in self.stack)
        return self._list_items(paths_hashable, field)


    @lru_cache(maxsize=128)
    def _list_items(self, paths, field=None):
        batch = list()
        for path in paths:
            last_is_leaf = [p.is_leaf for p in path[-2:]]
            if last_is_leaf == [True, True]: # second-last item is also leaf
                auto_field = 'path'
                path, value = path[:-1], path[-1].step
            elif last_is_leaf and last_is_leaf[-1] == True:  # only the last item is leaf
                auto_field = 'value'
                value = True
            else:
                auto_field = 'key'
                value = False
            steps = (p.step for p in path)
            batch.append((steps, value))

        results = self.cache.gets(
            attrs = [field or auto_field, 'is_leaf'],  # depends only on the last path
            filter_params = batch,
        )
        return OrderedDict(sorted(results))


    def emptyline(self):
        '''Do nothing on empty command line'''


    def do_recache(self, line=''):
        '''Reread documents from disk to browser cache'''
        try:
            Args(line, no_value=True)
        except ArgumentError as e:
            print('recache: {}'.format(e.message))
            return
        self._list_items.cache_clear()
        self.cache.update_timestamp()
        self.cache.add(directory=self.directory)
        self.cache.drop_outdated()


    def do_and(self, line=''):
        '''Append new AND query'''
        try:
            args = Args(line, no_value=True)
        except ArgumentError as e:
            print('and: {}'.format(e.message))
            return
        self.stack.append(self.path[:])


    def do_ls(self, line, field=None):
        '''Show possible branches to go from current position'''
        try:
            args = Args(line, no_value=True)
        except ArgumentError as e:
            print('ls: {}'.format(e.message))
            return
        items = self.get_pathitems(field)
        width = int(log10(len(items))) + 1
        template = '{num:>%s}: {item}' % width
        for num, item in enumerate(items, 1):
            print(template.format(**locals()))


    def do_files(self, line=''):
        '''Show files that match the current query'''
        self.do_ls(line, field='path')


    def do_cd(self, line):
        '''Go one level deeper into data hierarchy'''
        try:
            args = Args(line, single_value=True)
        except ArgumentError as e:
            print('cd: {}'.format(e.message))
            return

        args.positional_from(self.path_items)
        target = args[0]

        if target in self.path_items:
            if [p.is_leaf for p in self.path[-2:]] == [True, True]:
                print('cd: can not go any deeper')
            else:
                self.path.append(PathItem(target, self.path_items[target]))
        elif target == '..':
            self.do_up()
        else:
            print('cd: can not browse {!r}'.format(target))


    def do_up(self, line=''):
        '''Go up one level in hierarchy'''
        try:
            args = Args(line, no_value=True)
        except ArgumentError as e:
            print('up: {}'.format(e.message))
            return
        try:
            self.path.pop()
        except IndexError:  # already at top level
            pass


    def do_pwd(self, line=''):
        '''Show path to current position in data hierarchy'''
        try:
            args = Args(line, no_value=True)
        except ArgumentError as e:
            print('pwd: {}'.format(e.message))
            return
        for path in self.stack:
            print('/' + '/'.join(p.step for p in path))


    def do_debug(self, line=''):
        '''Launch Python debugger'''
        import pdb; pdb.set_trace()


    def do_exit(self, line):
        '''Exit interactive document browser'''
        return True


    do_EOF = do_exit



class ArgumentError(ValueError):
    '''Raised when a command receives invalid arguments from user'''

    @property
    def message(self):
        '''Fast access to the exception message'''
        if self.args:
            return self.args[0]



class Args:
    '''
    Handle command line arguments in interactive shell
    '''

    POSITIONAL = re.compile(r'^\$([0-9+])$')


    def __init__(self, line, single_value=False, no_value=False):
        '''Parse argument string'''
        self.raw = line
        self.argv = shlex.split(self.raw)
        if single_value and len(self.argv) != 1:
            raise ArgumentError('expected one argument, but got {}: {}'.format(
                len(self.argv), self.raw
            ))
        if no_value and self.argv:
            raise ArgumentError('expected no arguments, but got: {}'.format(
                self.raw
            ))


    def __getitem__(self, index):
        return self.argv[index]


    def positional_from(self, sequence):
        '''Replace positional references with sequence values'''
        for arg in sorted(self.argv):
            match = self.POSITIONAL.match(arg)
            if match:
                position = int(match.groups()[0])
                index = self.argv.index(arg)
                try:
                    self.argv[index] = next(islice(sequence, position-1, position))
                except StopIteration:
                    pass
