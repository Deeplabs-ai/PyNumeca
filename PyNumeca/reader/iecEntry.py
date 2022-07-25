import re
from PyNumeca.reader.numecaEntry import numecaEntry
class iecEntry(numecaEntry):
    def __init__(self):
        super(iecEntry, self).__init__()

    def parseSimpleEntry(self,string):
        if string == "\n":
            self.leadingSpaceString = ""
            self.key = ""
            self.keyTagSpaceString = ""
            self.tag = ""
            self.tagValueSpaceString = ""
            self.value = ""
            self.trailingSpaceString = "\n"
            return
        #splitPattern = '[\s]{2,}|(?<=[0-9])[\s]+(?=[0-9])|\b[\s]+$'
        splitPattern = '[\s]{2,}|(?<=\d)[\s]+(?=-?\d)|\b[\s]+$'
        tokenize = string.split()

        if (len(tokenize) > 2 and "NI_BEGIN" not in string and "VERTEX" not in string):
            tokenize = re.split(splitPattern,string.strip())
            spaces = re.findall(splitPattern, string.strip())
        else:
            spaces = re.findall('\s+', string.strip())



        self.key = tokenize[0]
        self.leadingSpaceString = re.match(r'^(\s*)', string).group(1)

        self.trailingSpaceString = re.search(r'(\s*)$', string).group(1)
        # Verifica per i parametri, da estendere in futuro se necessario
        parameterCheck = re.findall('^[a-zA-z]*(,[A-Z])(,[0-9])',string.strip(' '))
        if (len(tokenize) == 1):
            self.tag = ""
            self.value = ""
            self.keyTagSpaceString = ""
            self.tagValueSpaceString = ""
        elif (string.lstrip(' ').startswith(('*','#'))):
            self.tag = ""
            self.value = ""
            self.keyTagSpaceString = ""
            self.tagValueSpaceString = ""
            self.key = string.lstrip(' ')[:-1]
        elif (len(tokenize) == 2):
            self.tag = ""
            self.keyTagSpaceString = ""
            self.value = tokenize[1]
            self.tagValueSpaceString = spaces[0]
        elif (len(tokenize) > 2):
            self.value = []
            self.tagValueSpaceString = []
            if (tokenize[1].replace('.','',1).replace('-','',2).replace('E','',1).replace('e','',1).isnumeric()):
                self.tag = ""
                self.keyTagSpaceString = ""
                for idx,token in enumerate(tokenize[1:]):
                    self.value.append(token)
                    self.tagValueSpaceString.append(spaces[idx])
            else:
                self.tag = tokenize[1]
                self.keyTagSpaceString = spaces[0]
                for idx,token in enumerate(tokenize[2:]):
                    self.value.append(token)
                    self.tagValueSpaceString.append(spaces[idx - 1])

        #if ("0.176764989579553" in string or "0.0032820608466864" in string):
            #print (tokenize)



        else:
            raise RuntimeError

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

