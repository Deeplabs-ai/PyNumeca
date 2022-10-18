from PyNumeca.reader.iecEntry import iecEntry
import numpy as np
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
        self.R = []
        self.THETA = []

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

    def updateArraysCyl(self, newR, newTHETA, newZ):
        if (len(newR) != len(newTHETA) or len(newTHETA) != len(newZ)):
            print ("ERRORE")
            exit()
        self.numberOfPointsInt = len(newR)
        self.numberOfPointsEntry.key = str(self.numberOfPointsInt)
        self.R = newR
        self.THETA = newTHETA
        self.Z = newZ
        for index in range(len(newR)):
            self.X[index] = self.R[index] * np.cos(self.THETA[index])
            self.Y[index] = self.R[index] * np.sin(self.THETA[index])





