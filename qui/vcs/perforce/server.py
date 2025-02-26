"""
    Perforce server stuff
"""

from P4 import P4

debug = False


class CustomP4Adapter(P4):
    """
    Class to prevent unwanted disconnection from the perforce server if with
    statements are used imbricated.
    """

    def __init__(self):
        self.__dict__['with_scope_count'] = 0
        super().__init__()

    def increment_scope_count(self):
        self.__dict__['with_scope_count'] += 1

    def decrement_scope_count(self):
        self.__dict__['with_scope_count'] -= 1

    def __enter__(self):
        self.increment_scope_count()
        if debug is True:
            print("DBG - Scope Enter", self.__dict__, self)

        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.decrement_scope_count()
        if debug is True:
            print("DBG - Scope Exit", self.__dict__, self)

        if self.__dict__['with_scope_count'] <= 0:
            if debug is True:
                print("DBG - Closing connection", self)

            return super().__exit__(exc_type, exc_val, exc_tb)


def connect(env=None, p4_adapter=None):
    """
    Return a P4 adapter.
    `env` can be a dict with environment variable overrides.
    `env` can also be a dict such as returned by
    perforce.current_configuration_dict function.

    # Update 2021/04/27:
    `p4_adapter` is an already existing P4 adapter or None.
    If it is NOT None it is returned by the function after ensuring it is
    connected.
    Note:
    It is done to more easily reuse existing connections with the python 'with'
    statement.
    Example:
        # Without it you should have to write this if you want your function
        # to create a connection if not provided or reuse an existing connection
        # passed as an argument.
        def my_perforce_func(p4_adapter=None, env=None):
            if not p4_adapter:
                with server.connect(env=env) as p4:
                    with p4.at_exception_level(p.RAISE_NONE):
                        return p4.run('info')
            else:
                with p4_adapter.at_exception_level(p4_adapter.RAISE_NONE):
                    return p4_adapter.run('info')

        # Now you should be able to achieve the same behaviour with only this.
        def my_perforce_func(p4_adapter=None, env=None):
            with server.connect(env=env, p4_adapter=p4_adapter) as p4:
                with p4.at_exception_level(p4.RAISE_NONE):
                    return p4.run('info')
    """
    global debug
    import os

    if p4_adapter is not None:
        if p4_adapter.connected() is False:
            p4_adapter.connect()

        if debug is True:
            print("DBG - Reusing connection", p4_adapter)

        return p4_adapter

    backup_env = {}
    if env is not None:
        env = dict(env)  # make a copy
        if 'P4CONFIG' in os.environ:
            backup_env['P4CONFIG'] = os.environ['P4CONFIG']
            del os.environ['P4CONFIG']

        if 'P4ROOT' in os.environ:
            backup_env['P4ROOT'] = os.environ['P4ROOT']
            del os.environ['P4ROOT']

        for k, v in dict(env).items():
            # Try to be friendly with dict returned from perforce.current_configuration_dict
            if k in ['api_level',
                     'client',
                     'connected',
                     'cwd',
                     'editor',
                     'password',
                     'port',
                     'server_level',
                     'user',]:
                # ignore these values
                if k in ['api_level', 'connected', 'cwd', 'server_level']:
                    del env[k]
                    continue

                del env[k]
                k = str("P4{}".format(k.upper()))
                env[k] = v

            if k in os.environ:  # Make a backup of the value f necessary
                backup_env[k] = os.environ[k]

            os.environ[k] = v

    adapter = CustomP4Adapter()  # P4()
    # adapter.exception_level = 0 ???????? use the default for the moment ...
    adapter.connect()
    # BUGFixing API HACK
    # DO NOT REMOVE THE CODE LINE BELOW:
    # P4USER and P4CLIENT values are not fixed in the adapter yet and therefore
    # does not contain the current environment ...
    adapter.user, adapter.client
    # ... and now they are.
    if backup_env != {}:  # cleaning env and restoring values if necessary
        for k in env:
            if k in backup_env:
                os.environ[k] = backup_env[k]

            else:
                del os.environ[k]

        if 'P4ROOT' in backup_env:
            os.environ[str('P4ROOT')] = backup_env['P4ROOT']

        if 'P4CONFIG' in backup_env:
            os.environ[str('P4CONFIG')] = backup_env['P4CONFIG']

    return adapter
