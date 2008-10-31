import martian

class ConfigurationProfile(object):
    """Subclass this to create custom profiles.
    use the name directive so it will be automaticly
    registered in the framework:

    class MyConfiguration(ConfigurationProfile):
        name('my_configuration')
        
    """
    martian.baseclass()

    def __init__(self, log):
        self.log = log

    def databaseUpdaterFactory(self):
        raise NotImplementedError
    
    def contentProviderFactory(self):
        raise NotImplementedError

    def serverFactory(self):
        raise NotImplementedError
        
    def requestFactory(self):
        raise NotImplementedError

class MataDataPrefix(object):
    martian.baseclass()

class name(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    
