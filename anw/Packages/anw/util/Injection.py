# Derived from http://planet.open4free.org/tag/dependency%20injection/
# I probably made it worse d'oh
import logging


class Container(object):
    implementations = {}
    instances = {}
    alwaysNew = {}
    
    def __init__(self):
        pass
 
    @classmethod
    def addComponent(cls, interface, implementation=None, alwaysNew=False):
        cls.implementations[interface] = implementation or interface
        logging.info("interface: %s implementation: %s alwaysNew: %d"%(interface, implementation, alwaysNew))
        cls.alwaysNew[interface] = alwaysNew

    @classmethod
    def getComponent(cls, interface):
        if interface in cls.instances and cls.alwaysNew[interface] == False:
            return cls.instances[interface]
        if interface not in cls.implementations:
            return None
 
        c = cls.implementations[interface]
        instance = cls.instances[interface] = c.__new__(c)
 
        instance.__init__()
        return instance

class Services(object):
    """ 
    This is used when we want to call methods on other dependencies
    """
    
    @classmethod
    def inject(cls, interface):
        return Container.getComponent(interface)
    @classmethod
    def register(cls, interface, implementation=None, alwaysNew=False):
        """ Pass true to alwaysNew if you don't want singletons """
        Container.addComponent(interface, implementation, alwaysNew)
    
