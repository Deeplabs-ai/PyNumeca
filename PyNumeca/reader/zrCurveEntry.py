from PyNumeca.reader.iecGroup import iecGroup
class zrCurveEntry(iecGroup):
    def __init__(self, *args):
        super(zrCurveEntry, self).__init__()
        self.curveType = ""
        self.numberOfPoints = 0
        self.Z = []
        self.R = []
        self.leadingSpaceStringArray = ""
        self.trailingSpaceStringArray = "\n"
        self.middleSpaceStringArray = ""
        self.leadingSpaceStringHeader = ""
        self.trailingSpaceStringHeader = "\n"
        self.headerEntry = None
        self.footerEntry = None

        if len(args) > 0 and isinstance(args[0],iecGroup):
            self.headerEntry = list(args[0].items())[0][1]
            self.footerEntry = list(args[0].items())[-1][1]
            self.curveType = list(args[0].items())[1][1]
            self.numberOfPoints = int(list(args[0].items())[2][1].key)
            for i in range(self.numberOfPoints):
                self.Z.append(float(list(args[0].items())[3 + i][1].key))
                self.R.append(float(list(args[0].items())[3 + i][1].value))
            self.leadingSpaceStringArray = list(args[0].items())[-2][1].leadingSpaceString
            self.trailingSpaceStringArray = list(args[0].items())[-2][1].trailingSpaceString
            self.middleSpaceStringArray = list(args[0].items())[-2][1].tagValueSpaceString
            self.leadingSpaceStringHeader = list(args[0].items())[0][1].leadingSpaceString
            self.trailingSpaceStringHeader = list(args[0].items())[0][1].trailingSpaceString

    def addPoint(self,*args):
        if len(args) == 1 and isinstance(args[0],tuple):
            self.addPointUpdateLists(args[0][0], args[0][1])
        elif len(args) == 2 and isinstance(args[0],float) and isinstance(args[1],float):
            self.addPointUpdateLists(args[0], args[1])

    def addPointUpdateLists(self,Z,R):
        self.Z.append(Z)
        self.R.append(R)
        self.numberOfPoints += 1
        list(self.items())[2][1].key = str(self.numberOfPoints)

    def removePoint(self, *args):
        self.Z.pop(*args)
        self.R.pop(*args)
        self.numberOfPoints -= 1
        list(self.items())[2][1].key = str(self.numberOfPoints)

    def outputString(self):
        outputString = ""
        outputString += self.headerEntry.outputString()
        outputString += self.curveType.outputString()
        outputString += self.leadingSpaceStringArray + str(self.numberOfPoints) + self.trailingSpaceStringArray
        for i in range(self.numberOfPoints):
            outputString += self.leadingSpaceStringArray + str(self.Z[i]) + \
                            self.middleSpaceStringArray + str(self.R[i]) + \
                            self.trailingSpaceStringArray
        outputString += self.footerEntry.outputString()
        return (outputString)

    def append(self,new_ZR):
        self.numberOfPoints += new_ZR.numberOfPoints -1
        self.Z.extend(new_ZR.Z[1:])
        self.R.extend(new_ZR.R[1:])

    def updateArrays(self,newZ,newR):
        if (len(newZ) != len(newR)):
            print("ERRORE")
            exit()
        self.numberOfPoints = len(newZ)
        self.Z = newZ
        self.R = newR

    def uniformIncreasePointsNumber(self,n_points):
        Z2 = self.Z.pop()
        Z1 = self.Z.pop()
        R2 = self.R.pop()
        R1 = self.R.pop()
        for i in range(int(n_points+1)):
            self.R.append((R2 - R1) / int(n_points) * i + R1)
            self.Z.append((Z2 - Z1) / int(n_points) * i + Z1)
        self.numberOfPoints = int(n_points)
