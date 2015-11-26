# coding: utf-8
_formclasses = {}

def register(c):
    cid = c.__module__ + "." + c.__name__
    _formclasses[cid] = c

class formfield(object):
    def __init__(self, celestatype, caption=None):
        self.celestatype = celestatype
        self.caption = caption
        self.fget = None
        self.fset = None

    def __call__(self, f):
        name = f.__name__
        if self.caption is None:
            self.caption = name
        self.fget = f        
        return self
    
    def setter(self, f):
        self.fset = f
        return self
    
    def __get__(self, instance, owner):
        return self.fget(instance)
    
    def __set__(self, instance, value):
        if not(self.fset is None):
            return self.fset(instance, value)
        else:
            raise Exception('"%s" is a read-only field in form %s' % (self.caption, instance.__class__.__name__))

def form(cls):
    cls._properties = {}
    for name, method in cls.__dict__.iteritems():
        if method.__class__ == formfield:
            cls._properties[name] = method
    register(cls)
    return cls

