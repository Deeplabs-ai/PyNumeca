from PyNumeca.reader.iecEntry import iecEntry
from PyNumeca.reader.iecGroup import iecGroup
from collections import OrderedDict
from PyNumeca.reader.zrCurveEntry import zrCurveEntry
from PyNumeca.reader.niBladeGeometryEntry import niBladeGeometryEntry
import numpy as np
import re
class numecaParser(OrderedDict):
    def __init__(self,filename=""):
        self.fileName = filename
        self.stringData = ""
        self.parsing()

        if (filename!= ""):
            self.load(filename)

    def load(self,filename):
        self.fileName = filename
        try:
            with open(self.fileName, 'r') as file:
                self.stringData = file.readlines()
        except Exception as e:
            self.errorNotification(e)
        self.parsing()

    def extractD3DParametersString(self):
        outputString = ""
        try:
            number_of_parameters = self['ROOT']\
                                       ["DESIGN3D_COMPUTATION_0"]\
                                       ["DATABASE_GENERATION_MINAMO_0"]\
                                       ["SIMULATION_TASK_MANAGER_0"]\
                                       ["SIMULATION_TASKS_0"]\
                                       ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"]\
                                       ["PARAMETRIC_LAYER_0"]\
                                       ["PARAMETERS_0"]\
                                       ["NUMBER_OF_PARAMETERS"].value

            outputString += number_of_parameters + "\n"

            for key, value in self['ROOT']\
                                  ["DESIGN3D_COMPUTATION_0"]\
                                  ["DATABASE_GENERATION_MINAMO_0"]\
                                  ["SIMULATION_TASK_MANAGER_0"]\
                                  ["SIMULATION_TASKS_0"]\
                                  ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"]\
                                  ["PARAMETRIC_LAYER_0"]\
                                  ["PARAMETERS_0"].items():
                if ("PARAMETER_" in key):
                    outputString += value["NAME"].value + "\n"

            return (outputString)

        except:
            raise CustomError

    def extractD3DParametersList(self):
        outputList = []
        try:
            for key, value in self['ROOT']\
                                  ["DESIGN3D_COMPUTATION_0"]\
                                  ["DATABASE_GENERATION_MINAMO_0"]\
                                  ["SIMULATION_TASK_MANAGER_0"]\
                                  ["SIMULATION_TASKS_0"]\
                                  ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"]\
                                  ["PARAMETRIC_LAYER_0"]\
                                  ["PARAMETERS_0"].items():
                if ("PARAMETER_" in key):
                    outputList.append(value["NAME"].value)

            return (outputList)
        except:
            raise CustomError

    def createD3DDefaultParameter(self):
        stringlist = []
        stringlist.append("                     NI_BEGIN\tPARAMETER\n")
        stringlist.append("                        NAME                           DEFAULT\n")
        stringlist.append("                        PARAMETRIC_TYPE                DOUBLE\n")
        stringlist.append("                        LIMIT_MIN                      -1000000000\n")
        stringlist.append("                        LIMIT_MAX                      1000000000\n")
        stringlist.append("                        VALUE                          0.002\n")
        stringlist.append("                        VALUE_MIN                      0.001\n")
        stringlist.append("                        VALUE_MAX                      0.003\n")
        stringlist.append("                        VALUE_REF                      1\n")
        stringlist.append("                        NB_LEVELS                      2\n")
        stringlist.append("                        QUANTITY_TYPE                  VALUE\n")
        stringlist.append("                        UNCERTAIN                      FALSE\n")
        stringlist.append("                        REDUCTION                      FALSE\n")
        stringlist.append("                     NI_END\tPARAMETER\n")
        return (self.deepTree(stringlist,0))

    def createD3DParameter(self,name,type,value,min=None,max=None):
        newParameter,_ = self.createD3DDefaultParameter()
        newParameter["NAME"].value = name
        newParameter["PARAMETRIC_TYPE"].value = type
        newParameter["VALUE"].value = value
        if min is not None and max is not None:
            newParameter["VALUE_MIN"].value = min
            newParameter["VALUE_MAX"].value = max
        else:
            newParameter["VALUE_MIN"].value = value
            newParameter["VALUE_MAX"].value = value
        return (newParameter)

    def addD3DParameter(self, *arg):
        parametersLayer = self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
            ["PARAMETRIC_LAYER_0"] \
            ["PARAMETERS_0"]

        if (len(arg)==1 and isinstance(arg[0],iecGroup)):
            newParameter = arg[0]
        elif (len(arg)==3):
            newParameter = self.createD3DParameter(arg[0],arg[1],arg[2])
        elif (len(arg)==5):
            newParameter = self.createD3DParameter(arg[0], arg[1], arg[2], arg[3], arg[4])
        else:
            raise CustomError

        number_of_parameters = parametersLayer["NUMBER_OF_PARAMETERS"].value
        new_number_of_parameters = str(int(number_of_parameters)+1)
        parametersLayer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

        n = 0
        newGroupName = "PARAMETER" + "_" + str(n)
        while newGroupName in parametersLayer:
            n += 1
            newGroupName = "PARAMETER" + "_" + str(n)

        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
            ["PARAMETRIC_LAYER_0"] \
            ["PARAMETERS_0"] = self.insert_key_value(parametersLayer,newGroupName, "NI_END_PARAMETERS",newParameter)

    def removeD3DParameter(self,number=None):
        parametersLayer = self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
            ["PARAMETRIC_LAYER_0"] \
            ["PARAMETERS_0"]
        number_of_parameters = parametersLayer["NUMBER_OF_PARAMETERS"].value

        if (int(number_of_parameters)>0 and number is None):
            new_number_of_parameters = str(int(number_of_parameters)-1)
            parametersLayer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

            n = 0
            lastGroupName = "PARAMETER" + "_" + str(n)
            while lastGroupName in parametersLayer:
                n += 1
                lastGroupName = "PARAMETER" + "_" + str(n)
            n -= 1
            lastGroupName = "PARAMETER" + "_" + str(n)

            self['ROOT'] \
                ["DESIGN3D_COMPUTATION_0"] \
                ["DATABASE_GENERATION_MINAMO_0"] \
                ["SIMULATION_TASK_MANAGER_0"] \
                ["SIMULATION_TASKS_0"] \
                ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
                ["PARAMETRIC_LAYER_0"] \
                ["PARAMETERS_0"].pop(lastGroupName)

        elif (int(number_of_parameters)>0 and (isinstance(number, int) or isinstance(number, str))):

            new_number_of_parameters = str(int(number_of_parameters)-1)
            parametersLayer["NUMBER_OF_PARAMETERS"].value = new_number_of_parameters

            if (str(number).isdigit()):
                lastGroupName = "PARAMETER" + "_" + str(number)
            elif (number in self.extractD3DParametersList()):
                lastGroupName = ""
                for key, value in parametersLayer.items():
                    if ("PARAMETER_" in key and number == value["NAME"].value):
                        lastGroupName = key
            else:
                raise CustomError

            self['ROOT'] \
                ["DESIGN3D_COMPUTATION_0"] \
                ["DATABASE_GENERATION_MINAMO_0"] \
                ["SIMULATION_TASK_MANAGER_0"] \
                ["SIMULATION_TASKS_0"] \
                ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
                ["PARAMETRIC_LAYER_0"] \
                ["PARAMETERS_0"].pop(lastGroupName)

        else:
            pass

    def insert_key_value(self, a_dict, key, pos_key, value):
        new_dict = iecGroup()
        for k, v in a_dict.items():
            if k == pos_key:
                new_dict[key] = value  # insert new key
            new_dict[k] = v
        return new_dict

    def parsing(self):
        if isinstance(self.stringData,list) and "GEOMETRY TURBO" in self.stringData[0]:
            self.stringData[0] = "GEOMETRY-TURBO\n"
        self['ROOT'], temp = self.deepTree(self.stringData,0)
        self['ROOT'] = self.deepReorderZRcurve(self['ROOT'])
        #self['ROOT'] = self.deepReorderNiBladeGeometry(self['ROOT'])

    def deepReorderZRcurve(self, group):
        newGroup = iecGroup()
        for key, value in group.items():
            if (isinstance(value, iecGroup) and "zrcurve" in (list(value.items()))[0][0]):
                newGroup[key] = zrCurveEntry(value)
            elif (isinstance(value, iecGroup) and any(x in (list(value.items()))[0][0] for x in ["nibladegeometry", "NIBLADEGEOMETRY"])):
                newGroup[key] = niBladeGeometryEntry(value)
                #print (key)
                #newGroup[key] = self.deepReorderZRcurve(value)
            #    newGroup[key] = niBladeGeometryEntry(value)
            elif (isinstance(value, iecGroup)):
                newGroup[key] = self.deepReorderZRcurve(value)
            else:
                newGroup[key] = value
        return newGroup

    def deepTree(self, stringData,lineIndex):
        newcall = True
        group = iecGroup()
        while lineIndex < len(stringData):
            lineString = stringData[lineIndex]
            entry = iecEntry()
            entry.parseSimpleEntry(lineString)
            if (newcall and "NI_BEGIN" in lineString):
                #key = entry.key + "_" + entry.value
                if (isinstance(entry.value, list)):
                    key = entry.key + "_" + entry.tag + "_" + entry.value[0]
                else:
                    key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                lineIndex += 1
            elif (lineIndex==0 and entry.key == "GEOMETRY-TURBO"):
                stringData[0] = "GEOMETRY TURBO\n"
                groupName = "GEOMTURBO"
                group[groupName], lineIndex = self.deepTree(stringData,lineIndex)
            elif (lineIndex==0 and entry.value == "TURBO"):
                key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                lineIndex += 1
            elif (not newcall and "NI_BEGIN" in lineString):
                n = 0
                if (isinstance(entry.value, list)):
                    groupName = entry.tag + "_" + entry.value[0] + "_" + str(n)
                else:
                    groupName = entry.value + "_" + str(n)
                while groupName in group:
                    n += 1
                    if (isinstance(entry.value, list)):
                        groupName = entry.tag + "_" + entry.value[0] + "_"+ str(n)
                    else:
                        groupName = entry.value + "_" + str(n)

                group[groupName], lineIndex = self.deepTree(stringData,lineIndex)
            elif ("NI_END" in lineString):
                key = entry.key + "_" + entry.value
                group[key] = entry
                newcall = False
                lineIndex += 1
                return (group, lineIndex)
            elif (lineString.lstrip(' ').startswith(('*','#'))):
                n = 0
                key = 'comment' + "_" + str(n)
                while key in group:
                    n += 1
                    key = 'comment_' + str(n)
                group[key] = entry
                newcall = False
                lineIndex += 1
            elif (lineString == "\n"):
                n = 0
                key = 'empty_line' + "_" + str(n)
                while key in group:
                    n += 1
                    key = 'empty_line_' + str(n)
                group[key] = entry
                newcall = False
                lineIndex += 1
            else:
                key = entry.key
                n = 0
                while key in group:
                    n += 1
                    key = entry.key + "_" + str(n)
                group[key] = entry
                newcall = False
                lineIndex += 1

        return (group, lineIndex)

    def errorNotification(self,e):
        print (e)
        print ("ERRORE DI LETTURA")

    def outputString(self):
        return (self["ROOT"].outputString())

    def checkSetup(self):
        simulation_task_manager = self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"]

        simulation_task_manager["MODEL_EXTENSION"].value = "prt"
        simulation_task_manager["CFD_GEOM_EXTENSION"].value = "stp"

        for idx, group in enumerate((simulation_task_manager["SIMULATION_TASKS_0"]["SIMULATION_TASK_PARAM_GEOM_MODEL_0"],
                                     simulation_task_manager["SIMULATION_TASKS_0"]["SIMULATION_TASK_IGG_AUTOGRID_0"],
                                     simulation_task_manager["SIMULATION_TASKS_0"]["SIMULATION_TASK_EURANUS_TURBO_0"],
                                     simulation_task_manager["SIMULATION_TASKS_0"]["SIMULATION_TASK_CFVIEW_0"])):

            group["TASK_PROCESSING"].value = str(int(not(idx % 3))) #Activate only n.0 and n.3
            group["CHAIN_TYPE"].value = "EXTERNAL"
            group["IMPORT_SCRIPTS"].value = "1"

    def setParamScript(self,scriptName):
        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_PARAM_GEOM_MODEL_0"] \
            ["EXTERNAL_SCRIPT"].value = '"'+scriptName+'"'

    def setMeshScript(self,scriptName):
        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_IGG_AUTOGRID_0"] \
            ["EXTERNAL_SCRIPT"].value = '"'+scriptName+'"'

    def setSolverScript(self,scriptName):
        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_EURANUS_TURBO_0"] \
            ["EXTERNAL_SCRIPT"].value = '"'+scriptName+'"'

    def setPostProScript(self,scriptName):
        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_CFVIEW_0"] \
            ["EXTERNAL_SCRIPT"].value = '"'+scriptName+'"'

    def createPostProDefaultMacro(self):
        stringlist = []
        stringlist.append("                  NI_BEGIN\tUSER_DEFINED_MACRO\n")
        stringlist.append("                     SOLUTION_FILE                                      3D\n")
        stringlist.append("                     MACRO_FILE                                         myPath/myScript.py\n")
        stringlist.append("                     DATA_FILE                                          myScript.dat\n")
        stringlist.append("                     QUANTITY_NAME                                      myQuantity\n")
        stringlist.append("                     DIM                                                SCALAR\n")
        stringlist.append("                     ACTIVE                                             1\n")
        stringlist.append("                  NI_END\tUSER_DEFINED_MACRO\n")
        return (self.deepTree(stringlist,0))

    def createPostProMacro(self,scriptName):
        new_post_pro_macro, _ = self.createPostProDefaultMacro()
        new_post_pro_macro["MACRO_FILE"].value = "macro_CFV/"+scriptName
        new_post_pro_macro["DATA_FILE"].value = scriptName.rsplit('.', 1)[0]+".dat"
        new_post_pro_macro["QUANTITY_NAME"].value = scriptName.rsplit('.', 1)[0]
        return (new_post_pro_macro)

    def addPostProMacro(self, scriptName):
        postProMacroLayer = self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_CFVIEW_0"] \
            ["USER_DEFINED_MACROS_EXTERNAL_0"]

        if (isinstance(scriptName, iecGroup)):
            newPostProMacro = scriptName
        elif (isinstance(scriptName, str)):
            newPostProMacro = self.createPostProMacro(scriptName)
        else:
            raise CustomError

        n = 0
        newGroupName = "USER_DEFINED_MACRO" + "_" + str(n)
        while newGroupName in postProMacroLayer:
            n += 1
            newGroupName = "USER_DEFINED_MACRO" + "_" + str(n)

        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_CFVIEW_0"] \
            ["USER_DEFINED_MACROS_EXTERNAL_0"] = \
            self.insert_key_value(postProMacroLayer,newGroupName, "NI_END_USER_DEFINED_MACROS_EXTERNAL",newPostProMacro)

    def removePostProMacro(self, number=None):
        postProMacroLayer = self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_CFVIEW_0"] \
            ["USER_DEFINED_MACROS_EXTERNAL_0"]

        if (number is None):
            n = 0
            lastGroupName = "USER_DEFINED_MACRO" + "_" + str(n)
            while lastGroupName in postProMacroLayer:
                n += 1
                lastGroupName = "USER_DEFINED_MACRO" + "_" + str(n)
            n -= 1
            lastGroupName = "USER_DEFINED_MACRO" + "_" + str(n)

        elif (isinstance(number, int)):
            lastGroupName = "USER_DEFINED_MACRO" + "_" + str(number)

        else:
            raise CustomError

        self['ROOT'] \
            ["DESIGN3D_COMPUTATION_0"] \
            ["DATABASE_GENERATION_MINAMO_0"] \
            ["SIMULATION_TASK_MANAGER_0"] \
            ["SIMULATION_TASKS_0"] \
            ["SIMULATION_TASK_CFVIEW_0"] \
            ["USER_DEFINED_MACROS_EXTERNAL_0"].pop(lastGroupName)

    def exportNpyArray(self, rowNumber=0, bladeNumber=0):
        niBladeGeometry = self.retrieveNiBladeGeometry(rowNumber, bladeNumber)

        suction = []
        pressure = []
        for item in niBladeGeometry.suctionList:
            section = np.vstack([item.X, item.Y, item.Z, np.zeros(item.numberOfPointsInt)]).transpose()
            suction.append(section)
        for item in niBladeGeometry.pressureList:
            section = np.vstack([item.X, item.Y, item.Z, np.ones(item.numberOfPointsInt)]).transpose()
            section = np.flip(section, axis=0)
            pressure.append(section)
        return (np.array([(np.asarray(suction), np.asarray(pressure))],dtype=float))

    def importNpyArray(self, array,rowNumber=0, bladeNumber=0):
        # array shape (2,nSections,nPoints,4)
        niBladeGeometry = self.retrieveNiBladeGeometry(rowNumber, bladeNumber)
        nSectionsFromArray = array.shape[1]
        niBladeGeometry.setNumberOfSections(nSectionsFromArray)
        for idx, suction in enumerate(niBladeGeometry.suctionList):
            newList = array[0][idx].transpose().tolist()
            suction.updateArrays(newList[0], newList[1], newList[2])
        for idx, pressure in enumerate(niBladeGeometry.pressureList):
            newList = array[1][idx].transpose().tolist()
            pressure.updateArrays(newList[0][::-1], newList[1][::-1], newList[2][::-1])

    def retrieveNiBladeGeometry(self,rowNumber=0, bladeNumber=0):
        rowOccurence = -1
        bladeOccurence = -1
        rowKey = ""
        bladeKey = ""

        for key in self["ROOT"]["GEOMTURBO"].keys():
            if "nirow" in key or "NIROW" in key:
                rowOccurence +=1
                if rowOccurence == rowNumber:
                    rowKey = key

        for key in self["ROOT"]["GEOMTURBO"][rowKey].keys():
            if "NIBlade" in key or "NIBLADE" in key:
                bladeOccurence +=1
                if bladeOccurence == bladeNumber:
                    bladeKey = key

        if (rowKey == ""): print("Row not defined")
        if (bladeKey == ""): print("Blade not defined")

        if ("NIROW" in rowKey): niBladeGeometry = self["ROOT"]["GEOMTURBO"][rowKey][bladeKey]["NIBLADEGEOMETRY_0"]
        elif ("nirow" in rowKey): niBladeGeometry = self["ROOT"]["GEOMTURBO"][rowKey][bladeKey]["nibladegeometry_0"]
        else: print("ERROR")

        return niBladeGeometry





class CustomError(Exception):
    pass

