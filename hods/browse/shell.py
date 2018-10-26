'''
Interactive shell for browsing HODS documents
'''


from cmd import Cmd
from collections import namedtuple, OrderedDict
from functools import lru_cache

from hods.browse.cache import DocumentsReadOnlyCache


PathItem = namedtuple('PathItem', 'step,is_leaf')


class DocumentBrowser(Cmd):
    # TODO: parse commandline arguments from string

    intro = 'Interactive document browser for HODS (https://hods.ml)'
    prompt = '(hods) > '


    def __init__(self, cache_file, browse_directory, *a, **ka):
        '''Initialize document browser with a cache file'''
        super().__init__(*a, **ka)
        self.directory = browse_directory
        self.path = list()  # sequence of PathItem tuples
        self.cache = DocumentsReadOnlyCache(cache_file)
        self.cache.add(directory=self.directory)
        self.cache.drop_outdated()


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
        elif last_is_leaf == [False, True]:  # only the last item is leaf
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


    def do_ls(self, args):
        print('\n'.join(self.path_items.keys()))


    def do_cd(self, target):
        if target in self.path_items:
            if [p.is_leaf for p in self.path[-2:]] == [True, True]:
                print('cd: can not go any deeper')
            else:
                self.path.append(PathItem(target, self.path_items[target]))
        elif target == '..':
            self.do_up()
        else:
            print('cd: can not browse {!r}'.format(target))


    def do_up(self, args=None):
        '''Go up one level in hierarchy'''
        try:
            self.path.pop()
        except IndexError:  # already at top level
            pass


    def do_pwd(self, args=None):
        '''Show path to current position in data hierarchy'''
        print('/' + '/'.join(p.step for p in self.path))


    def do_debug(self, args=None):
        '''Launch Python debugger'''
        import pdb; pdb.set_trace()


    def do_exit(self, args):
        '''Exit interactive document browser'''
        return True


    do_EOF = do_exit
