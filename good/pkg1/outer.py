
class outer(object):

    def __init__(self):
        from inner import inner
        self.inner = inner()
