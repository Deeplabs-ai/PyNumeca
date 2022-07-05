from PyNumeca.reader.iecGroup import iecGroup
from PyNumeca.reader.sectionEntry import sectionEntry
import copy
class niBladeGeometryEntry(iecGroup):
    def __init__(self, *args):
        super(niBladeGeometryEntry, self).__init__()
        self.numberOfSectionsInteger = 0
        self.suctionHeader = None
        self.sectionalHeader = None
        self.numberOfSectionsEntry = None
        self.headerList = []
        self.suctionList = []
        self.pressureList = []
        self.footer = None


        if len(args) > 0 and isinstance(args[0],iecGroup):    # Deve essere un gruppo NiBladeGeometry
            entryIndex = 0
            totalLength = len(list(args[0].items()))
            while(True):
                if entryIndex < totalLength:
                    key, value = list(args[0].items())[entryIndex]
                else:
                    break
                if ("suction" in key):
                    self.suctionHeader = value
                    self.sectionalHeader = list(args[0].items())[entryIndex+1][1]
                    self.numberOfSectionsEntry = list(args[0].items())[entryIndex+2][1]
                    self.numberOfSectionsInteger = int(self.numberOfSectionsEntry.key)

                    for item in range(self.numberOfSectionsInteger):
                        previousPoints = 0
                        for subItem in range(item):
                            previousPoints += self.suctionList[subItem].numberOfPointsInt + 3
                        section = self.extractSection(args[0],entryIndex+3+previousPoints)

                        self.suctionList.append(section)

                    pressureRowIndex = entryIndex + previousPoints + self.suctionList[-1].numberOfPointsInt + 6

                    self.pressureHeader = list(args[0].items())[pressureRowIndex][1]

                    for item in range(self.numberOfSectionsInteger):
                        previousPoints = 0
                        for subItem in range(item):
                            previousPoints += self.pressureList[subItem].numberOfPointsInt + 3
                        section = self.extractSection(args[0], pressureRowIndex + previousPoints + 3)
                        self.pressureList.append(section)
                    entryIndex = pressureRowIndex + 6 + previousPoints + self.pressureList[-1].numberOfPointsInt
                    self.footer = list(args[0].items())[entryIndex][1]
                    break

                else:
                    self.headerList.append(value)

                entryIndex += 1

    def extractSection(self,entry, entryIndex):
        section = sectionEntry()
        section.headerComment = list(entry.items())[entryIndex][1]
        section.referenceFrame = list(entry.items())[entryIndex + 1][1]
        section.numberOfPointsEntry = list(entry.items())[entryIndex + 2][1]
        section.numberOfPointsInt = int(section.numberOfPointsEntry.key)
        section.leadingSpaceString = list(entry.items())[entryIndex + 3][1].leadingSpaceString
        section.trailingSpaceString = list(entry.items())[entryIndex + 3][1].trailingSpaceString
        section.X2YSpaceString = list(entry.items())[entryIndex + 3][1].tagValueSpaceString[0]
        section.Y2ZSpaceString = list(entry.items())[entryIndex + 3][1].tagValueSpaceString[1]
        for row in range(section.numberOfPointsInt):
            section.X.append(float(list(entry.items())[entryIndex + 3 + row][1].key))
            section.Y.append(float(list(entry.items())[entryIndex + 3 + row][1].value[0]))
            section.Z.append(float(list(entry.items())[entryIndex + 3 + row][1].value[1]))
        return section

    def outputString(self):
        outputString = ""
        for row in self.headerList:
            outputString += row.outputString()
        outputString += self.suctionHeader.outputString()
        outputString += self.sectionalHeader.outputString()
        outputString += self.numberOfSectionsEntry.outputString()
        for section in self.suctionList:
            outputString += section.outputString()
        outputString += self.pressureHeader.outputString()
        outputString += self.sectionalHeader.outputString()
        outputString += self.numberOfSectionsEntry.outputString()
        for section in self.pressureList:
            outputString += section.outputString()
        outputString += self.footer.outputString()

        return (outputString)

    def setNumberOfSections(self,number):
        diff = self.numberOfSectionsInteger - number
        self.numberOfSectionsInteger = number
        self.numberOfSectionsEntry.key = str(number)
        if (diff == 0):
            pass
        elif (diff < 0):
            for i in range(abs(diff)):
                self.suctionList.append(copy.deepcopy(self.suctionList[-1]))
                self.pressureList.append(copy.deepcopy(self.pressureList[-1]))
        elif (diff >0):
            del self.suctionList[(-1) * diff:]
            del self.pressureList[(-1) * diff:]
