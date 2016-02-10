# coding: utf-8
import ru.curs.lyra.LyraFormField as LyraFormField
import ru.curs.lyra.LyraFieldType as LyraFieldType
import ru.curs.lyra.UnboundFieldAccessor as UnboundFieldAccessor
import ru.curs.lyra.LyraFormProperties as LyraFormProperties

_formclasses = {}

def register(c):
    cid = c.__module__ + "." + c.__name__
    _formclasses[cid] = c

class formfield(object):
    def __init__(self, celestatype, 
                 caption=None, 
                 editable = True, 
                 visible = True,
                 required = False, 
                 scale = LyraFormField.DEFAULT_SCALE, 
                 width = -1):
        self.celestatype = celestatype
        self.caption = caption
        self.editable = editable
        self.visible = visible
        self.scale = scale
        self.width = width
        self.required = required
        self.fget = None
        self.fset = lambda instance, value: None

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
        return self.fset(instance, value)

def _createUnboundField(self, m, name):
    if not hasattr(self.__class__, "_properties"):
        raise Exception('Did you forget @form decorator for class %s?' % (self.__class__.__name__))
    ff = self.__class__._properties[name]
    if ff is None:
        return None
    acc = UnboundFieldAccessor(ff.celestatype, ff.fget, ff.fset, self)
    lff = LyraFormField(name, acc);
    m.addElement(lff);
    lff.setType(LyraFieldType.valueOf(ff.celestatype.upper()));
    lff.setCaption(ff.caption)
    lff.setEditable(ff.editable)
    lff.setVisible(ff.visible)
    lff.setScale(ff.scale)
    lff.setWidth(ff.width)
    lff.setRequired(ff.required)
    return lff
        
def _createAllUnboundFields(self, m):
    if not hasattr(self.__class__, "_properties"):
        raise Exception('Did you forget @form decorator for class %s?' % (self.__class__.__name__))
    for name in self.__class__._properties.keys():
        self._createUnboundField(m, name)
           
def _getId(self):
    return self.__class__.__module__ + "." + self.__class__.__name__

def _getFormProperties(self):
    return self.__class__._formproperties

class form(object):
    def __init__(self, profile=None, gridwidth=-1, gridheight = -1, defaultaction=None):
        lfp = LyraFormProperties()
        lfp.setProfile(profile)
        lfp.setGridwidth(gridwidth)
        lfp.setGridheight(gridheight)
        lfp.setDefaultaction(defaultaction)
        self.lfp = lfp
     
    def __call__(self, cls):   
        cls._formproperties = self.lfp;
        cls.getFormProperties = _getFormProperties
        cls._properties = {}
        for name, method in cls.__dict__.iteritems():
            if method.__class__ == formfield:
                cls._properties[name] = method
            elif name == 'get_properties_':
                ff = formfield(celestatype='VARCHAR')(method)
                ff.name = '_properties_'
                ff.caption = ff.name
                cls._properties[ff.name] = ff
        cls._createUnboundField = _createUnboundField
        cls._createAllUnboundFields = _createAllUnboundFields
        cls._getId = _getId
        register(cls)
        return cls

