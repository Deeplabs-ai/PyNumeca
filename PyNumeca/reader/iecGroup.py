from collections import OrderedDict
class iecGroup(OrderedDict):
    def __init__(self,*arg,**kw):
        super(iecGroup, self).__init__(*arg,**kw)
        if len(arg) > 0 and isinstance(arg[0],iecGroup):
            for key, value in arg[0].items():
                #super(iecGroup, self).__init__(key) = value
                self[key] = value

    def copy(self,fromObject):
        for key, value in fromObject.items():
            #super(iecGroup, self).__init__(key) = value
            self[key] = value

    def outputString(self):
        outputString = ""
        for key, value in self.items():
            outputString += value.outputString()
        return (outputString)
