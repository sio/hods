'''
Interactive shell for browsing HODS documents
'''


import shlex
from cmd import Cmd
from collections import namedtuple, OrderedDict
from functools import lru_cache

from hods.browse.cache import DocumentsReadOnlyCache


PathItem = namedtuple('PathItem', 'step,is_leaf')


class DocumentBrowser(Cmd):
    intro = 'Interactive document browser for HODS (https://hods.ml)'
    prompt = '(hods) > '


    def __init__(self, cache_file, browse_directory, *a, **ka):
        '''Initialize document browser with a cache file'''
        super().__init__(*a, **ka)
        self.directory = browse_directory
        self.path = list()  # sequence of PathItem tuples
        self.cache = DocumentsReadOnlyCache(cache_file)
        self.do_recache()


    @property
    def path_items(self):
        '''Content of the current branch'''
        return self._list_items(*self.path)


    @lru_cache(maxsize=128)
    def _list_items(self, *path):
        last_is_leaf = [p.is_leaf for p in path[-2:]]

        if last_is_leaf == [True, True]: # second-last item is also leaf
            field = 'path'
            path = path[:-1]
        elif last_is_leaf and last_is_leaf[-1] == True:  # only the last item is leaf
            field = 'value'
        else:
            field = 'key'

        results = self.cache.get(
            attrs    = [field, 'is_leaf'],
            steps    = (p.step for p in path),
            by_value = last_is_leaf[-1] if last_is_leaf else False,
        )
        return OrderedDict(results)


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


    def do_ls(self, line):
        '''Show possible branches to go from current position'''
        try:
            args = Args(line, no_value=True)
        except ArgumentError as e:
            print('ls: {}'.format(e.message))
            return
        print('\n'.join(self.path_items.keys()))


    def do_cd(self, line):
        '''Go one level deeper into data hierarchy'''
        try:
            target = Args(line, single_value=True).argv[0]
        except ArgumentError as e:
            print('cd: {}'.format(e.message))
            return
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
        print('/' + '/'.join(p.step for p in self.path))


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
