"""
    Perforce utilities.

Example
```python

def first_function(*args, p4_adapter=None, env=None, **kwargs):
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        # You can pass the p4_adapter to another function using a with statement
        # to reuse the connection to the perforce server.
        second_function(*args, env=env, p4_adapter=p4_adapter, **kwargs)


def second_function(*args, p4_adapter=None, env=None, **kwargs):
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        # You can modulate the exception level of the API
        # using a with statement as below.
        with p4_adapter.at_exception_level(P4.RAISE_NONE):
            p4_adapter.run('whatever')
        # Here the exception_level returns to whatever the
        # p4_adapter was at the beginnning of the function

from qui.vcs import perforce

with perforce.server.connect() as p4:
    first_function(p4_adapter=p4)
```
"""
import os

from pprint import pprint

from P4 import (
    P4,
    P4Exception,  # To have it accessible from perforce.P4Exception
)

from . import server

from datetime import datetime, timedelta


cache_timeout = timedelta(seconds=60)  # duration of the cache validity

__memcache = {
    # to store cached result, the p4 server thanking you for doing so.
    # str(path): {'result': dict(fstat_cmd_result), 'date': datetime.datetime(age)
}


def get_current_configuration_dict(p4_adapter=None):
    """
    Return the current P4 API adapter description into a dict.
    """
    with server.connect(p4_adapter=p4_adapter) as p4_adapter:
        ret = {
            "user": p4_adapter.user,
            "server_level": (
                p4_adapter.server_level if p4_adapter.connected() else None,
            ),
            "port": p4_adapter.port,
            "client": p4_adapter.client,
            "password": p4_adapter.password,
            "connected": p4_adapter.connected(),
            "cwd": p4_adapter.cwd,
            "editor": p4_adapter.env("P4EDITOR"),
            "api_level": p4_adapter.api_level,
        }
        return ret


def get_info(p4_adapter=None, env=None):
    """
    Return a dict containing the results from a `p4 info` command.
    """
    with server.connect(p4_adapter=p4_adapter, env=env) as p4_adapter:
        return p4_adapter.run('info')[0]


def is_file_perforced(file_path, p4_adapter=None, env=None):
    """
    Return True if file `file_path` is in perforce, False otherwise.
    Note: Does not work with directory name.
    """
    import os
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        with p4_adapter.at_exception_level(P4.RAISE_NONE):
            path = (
                os.path.realpath(file_path)
                if file_path[0:2] != "//"
                else file_path
            )
            return True if p4_adapter.run("have", path) else False


def is_under_client_root(path, p4_adapter=None, env=None):
    """
    Return True if path is under perforce client root, False otherwise.
    """
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        with p4_adapter.at_exception_level(P4.RAISE_NONE):
            path = os.path.realpath(path)
            client_root = os.path.realpath(get_info(p4_adapter=p4_adapter)['clientRoot'])
            return (client_root + os.path.sep) in path


def filter_perforced_filenames(paths, p4_adapter=None, env=None):
    """
    Returned filtered `paths` list with only the perforced paths.
    (Note: Only the client path is returned for each matching entry)
    """
    filtered_paths = []
    with server.connect(p4_adapter=p4_adapter, env=env) as p4_adapter:
        paths = get_project_paths_to_client_root(
            paths, p4_adapter=p4_adapter, env=env
        )
        for p in paths:
            if is_file_perforced(p, p4_adapter=p4_adapter, env=env) is True:
                filtered_paths.append(p)

    return filtered_paths


def get_depot_path(local_path, p4_adapter=None, env=None):
    """
    Return the local path from a perforce address, None if no mapping is found.
    Function use the default perforce settings to connect to the server or
    a connected p4_adapter if provided.
    Path directory can be found by putting a trailing slash in
    the local_path argument.
    """
    global __memcache, cache_timeout

    if local_path.endswith('/'):  # since p4 where only works on filename (0o)
        local_path += "__QUI_MARKER__"

    if local_path in __memcache:
        if datetime.now() - __memcache[local_path]['date'] < cache_timeout:
            result = __memcache[local_path]['result']
            return (
                result['depotFile'].split('__QUI_MARKER__')[0]
                if result is not None else None
            )

    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        with p4_adapter.at_exception_level(p4_adapter.RAISE_NONE):
            res = p4_adapter.run('where', local_path)

    __memcache[local_path] = {
        'result': res[0] if res != [] else None,
        'date': datetime.now()
    }
    return (
        __memcache[local_path]['result']['depotFile'].split('__QUI_MARKER__')[0]
        if res != [] else None
    )


def resolve_local_path_with_revision(path, ensure_perforced=False,
                                     p4_adapter=None, env=None):
    """
    Return the resolved perforce path //perforce_path#(rev) from path.
    If path is not already added, only the perforce path is returned
    or `path` if `ensure_perforced` is set to True.
    If path is outside the workspace file system, path is returned.
    """
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        if ensure_perforced is True:
            if is_file_perforced(path, p4_adapter=p4_adapter) is False:
                return path

        with p4_adapter.at_exception_level(p4_adapter.RAISE_NONE):
            res = p4_adapter.run('fstat', path)
            if res == []:
                res = get_depot_path(path, p4_adapter=p4_adapter)
                return path if res is None else res

            return "{}#{}".format(res[0]['depotFile'], res[0].get('haveRev', '-1'))


def get_local_path(perforce_path, p4_adapter=None, env=None):
    """
    Return the local path from a perforce address, None if no mapping is found.
    Function use the default perforce settings to connect to the server or
    a connected p4_adapter if provided.
    Path directory can be found by putting a trailing slash in
    the perforce_path argument.
    """
    global __memcache, cache_timeout

    if perforce_path.endswith('/'):  # since p4 where only works on filename (0o)
        perforce_path += "__QUI_MARKER__"

    if perforce_path in __memcache:
        if datetime.now() - __memcache[perforce_path]['date'] < cache_timeout:
            result = __memcache[perforce_path]['result']
            return (
                result['path'].split('__QUI_MARKER__')[0]
                if result is not None else None
            )

    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        with p4_adapter.at_exception_level(p4_adapter.RAISE_NONE):
            res = p4_adapter.run('where', perforce_path)

    __memcache[perforce_path] = {
        'result': res[0] if res != [] else None,
        'date': datetime.now()
    }
    return (
        __memcache[perforce_path]['result']['path'].split('__QUI_MARKER__')[0]
        if res != [] else None
    )


def get_current_user_pending_changelists_numbers(p4_adapter=None, env=None):
    """
    Return the list of all current user pending changelist numbers.
    """
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        return [
            c['change']
            for c in get_current_user_pending_changelists(p4_adapter=p4_adapter)
        ]


def get_current_user_pending_changelists(p4_adapter=None, env=None):
    """
    Return the list of all current user pending changelists.
    Changelists are dict object such as:
    {
        'change': str(),
        'changeType': str(),
        'client': str(),
        'desc': str(),
        'status': str(),
        'time': str(),
        'user': str()
    }
    """
    with server.connect(env=env, p4_adapter=p4_adapter) as p4_adapter:
        return sorted(
            [
                c
                for c in p4_adapter.run(
                    'changes', '--me', '-s', 'pending', '-c', p4_adapter.client
                )
            ],
            reverse=True,
            key=lambda x: int(x['change'])
        )


def has_pending_changelist(changelist_number, p4_adapter=None, env=None):
    """
    Return True if `changelist_number` is in current user pending CL list
    False otherwise.
    """
    pending_cls = get_current_user_pending_changelists_numbers(env=env, p4_adapter=p4_adapter)
    return str(changelist_number) in pending_cls


class CurrentUser(object):
    """
    Utility class for contextual metas retrieval based on
    the current perforce user.
    """
    @property
    def login(self):
        """
        Current perforce user name.
        """
        return get_current_configuration_dict()['user']

    @property
    def pending_changelist_numbers(self):
        """
        Current user pending changelists numbers.
        """
        return get_current_user_pending_changelists_numbers()

    @property
    def pending_changelists(self):
        """
        Current user pending changelists.
        """
        return get_current_user_pending_changelists()
