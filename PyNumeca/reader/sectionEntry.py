from PyNumeca.reader.iecEntry import iecEntry
class sectionEntry(iecEntry):
    def __init__(self, *args):
        super(sectionEntry, self).__init__()
        self.headerComment = None
        self.numberOfPointsInt = 0
        self.numberOfPointsEntry = iecEntry()
        self.referenceFrame = "XYZ"
        self.leadingSpaceString = ""
        self.X2YSpaceString = ""
        self.Y2ZSpaceString = ""
        self.trailingSpaceString = ""
        self.X = []
        self.Y = []
        self.Z = []

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def outputString(self):
        outputString = ""
        outputString += self.headerComment.outputString()
        outputString += self.referenceFrame.outputString()
        outputString += self.numberOfPointsEntry.outputString()
        for i in range(self.numberOfPointsInt):
            #print(len(self.X2YSpaceString),  len(self.Y2ZSpaceString[0]), len(self.Y2ZSpaceString[1]))
            #print (str(self.X[i]),"\n", str(self.Y[i]),"\n", str(self.Z[i]))
            outputString += self.leadingSpaceString + str(self.X[i]) + \
                            self.X2YSpaceString + str(self.Y[i]) + \
                            self.Y2ZSpaceString + str(self.Z[i]) + \
                            self.trailingSpaceString
        return outputString

    def updateArrays(self, newX, newY, newZ):
        if (len(newX) != len(newY) or len(newY) != len(newZ)):
            print ("ERRORE")
            exit()
        self.numberOfPointsInt = len(newX)
        self.numberOfPointsEntry.key = str(self.numberOfPointsInt)
        self.X = newX
        self.Y = newY
        self.Z = newZ


