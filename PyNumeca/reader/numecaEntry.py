class numecaEntry:
    def __init__(self,*args):
        self.leadingSpaceString = ""
        self.key = ""
        self.keyTagSpaceString = ""
        self.tag = ""
        self.tagValueSpaceString = ""
        self.value = None
        self.trailingSpaceString = ""
        if (len(args) > 0 and isinstance(args[0],numecaEntry)):
            self.leadingSpaceString = args[0].leadingSpaceString
            self.key = args[0].key
            self.keyTagSpaceString = args[0].keyTagSpaceString
            self.tag = args[0].tag
            self.tagValueSpaceString = args[0].tagValueSpaceString
            self.value = args[0].value
            self.trailingSpaceString = args[0].trailingSpaceString

    def copy(self,fromObject):
        self.leadingSpaceString = fromObject.leadingSpaceString
        self.key = fromObject.key
        self.keyTagSpaceString = fromObject.keyTagSpaceString
        self.tag = fromObject.tag
        self.tagValueSpaceString = fromObject.tagValueSpaceString
        self.value = fromObject.value
        self.trailingSpaceString = fromObject.trailingSpaceString

    def outputString(self):
        valueString = ""
        if (isinstance(self.value, str)):
            valueString += self.tagValueSpaceString + self.value
        elif (isinstance(self.value, list)):
            for idx,token in enumerate(self.value):
                valueString += self.tagValueSpaceString[idx] + token
        return (self.leadingSpaceString + self.key +
                self.keyTagSpaceString + self.tag +
                valueString + self.trailingSpaceString)

    def __repr__(self):
        valueString = ""
        if (isinstance(self.value, str)):
            valueString += str(len(self.tagValueSpaceString))+" "+ self.value + "\n"
        elif (isinstance(self.value, list)):
            for idx, token in enumerate(self.value):
                valueString += str(len(self.tagValueSpaceString[idx])) +" " + token + "\n"

        return (str(len(self.leadingSpaceString))+" "+ self.key + "\n" +
                str(len(self.keyTagSpaceString))+" "+ self.tag + "\n" +
                valueString)

    def __str__(self):
        valueString = ""
        if (isinstance(self.value, str)):
            valueString += self.value + "\n"
        elif (isinstance(self.value, list)):
            for idx, token in enumerate(self.value):
                valueString += self.tagValueSpaceString[idx] + token
            valueString += "\n"

        return (self.key + "\n" +
                self.tag + "\n" +
                valueString)
