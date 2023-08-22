# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import pandas as pd


class DxDiagInterpreter:
    def __init__(self, file):
        #os.system("dxdiag.exe /t")
        self.ramserial = str(os.system("wmic memorychip list full > ram.txt"))
        self.memcheck = str(os.system("wmic diskdrive get model, status > diskchk.txt"))
        self.dxdiagfile = "dxdiag.txt"
        self.ramfile = "ram.txt"
        self.diagDict = {}
        self.werDf = {}
        self.werDict = {}
        self.populate_data()

    def populate_data(self):
        dxfile = open(self.dxdiagfile, mode = 'r', encoding = 'utf-8-sig')

        dxlines = dxfile.readlines()

        section = 0
        keys = []
        values = []
        wercount = -1
        werKeys = []
        hdrivecount = -1
        for line in dxlines:
            if "------" in line:
                section +=1
            if ": " in line:
                i = 0
                for word in line:
                    if word == " ":
                        i+= 1
                    else:
                        break
                if section == 2:
                    keyEnd = line.index(": ")
                    keys.append(line[i:keyEnd])
                    values.append(line[keyEnd+2:-1])
                if section == 24:
                    keyEnd = line.index(": ")
                    if line[i:keyEnd] == "Drive":
                        hdrivecount += 1
                    keys.append(line[i:keyEnd])
                    values.append(line[keyEnd+2:-1])
                if section == 50:
                    keyEnd = line.index(": ")
                    if line[i:keyEnd] == "Event Name":
                        wercount += 1
                    keys.append(line[i:keyEnd])
                    werKeys.append(line[i:keyEnd])
                    values.append(line[keyEnd+2:-1])

        dxfile.close()
        ramfile = open(self.ramfile, mode = 'r', encoding = 'utf-16-le')
        ramlines = ramfile.readlines()
        for line in ramlines:
            if '=' in line:
                keyEnd = line.index("=")
                valueEnd = line.index("\n")
                keys.append(line[0:keyEnd])
                values.append(line[keyEnd + 1: valueEnd])

        diagDict = {}
        werDict = {}
        i = 0
        for key in keys:
            if key in diagDict:
                diagDict[key].append(values[i])
            else:
                diagDict.update({key:[values[i]]})
            i+=1
        for key in werKeys:
            werDict[key] = diagDict[key]

        i = 0
        if self.diagDict == diagDict:
            return
        else:
            for key in keys:
                if key in self.diagDict:
                    self.diagDict[key].append(values[i])
                else:
                    self.diagDict.update({key: [values[i]]})
                i += 1
            for key in werKeys:
                self.werDict[key] = self.diagDict[key]
            self.werDf = pd.DataFrame(werDict)
            print (self.diagDict)

    def filter_events_json(self, event_data, event_ids, fields=None):
        for evt in event_data:
            system_tag = evt.find("System", evt.nsmap)
            event_id = system_tag.find("EventID", evt.nsmap)
            if event_id.text in event_ids:
                event_data = evt.find("EventData", evt.nsmap)
                json_data = {}
                for data in event_data.getchildren():
                    if not fields or data.attrib["Name"] in fields:
                        # If we don't have a specified field filter list, print all
                        # Otherwise filter for only those fields within the list
                        json_data[data.attrib["Name"]] = data.text

                yield json_data
    def is_out_of_date(self):
        self.hardware = {'SSDs': pd.DataFrame() ,"HDDs": pd.DataFrame() ,"GPUs": pd.DataFrame(), "CPUs": pd.DataFrame(), "RAM": pd.DataFrame()}

        hddDatabase = pd.read_csv("userbenchmarkdb\HDD_UserBenchmarks.csv")
        ssdDatabase = pd.read_csv("userbenchmarkdb\SSD_UserBenchmarks.csv")
        cpuDatabase = pd.read_csv("userbenchmarkdb\CPU_UserBenchmarks.csv")
        gpuDatabase = pd.read_csv("userbenchmarkdb\GPU_UserBenchmarks.csv")
        ramDatabase = pd.read_csv("userbenchmarkdb\RAM_UserBenchmarks.csv")
        model = "NULL"

        for hsd in self.diagDict['Model']:
            if hsd == '':
                break
            count = 0
            fails = 0
            model = hsd.split(" ")
            for split in model:
                if len(model) <= 2:
                    hddRes = hddDatabase[hddDatabase["Model"].apply(str.upper).str.contains(split.upper())]
                    try:
                        self.hardware['HDDs'] = pd.concat([self.hardware['HDDs'], hddRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                if count % 2 == 0 and len(model) > 2:
                    hddRes = hddDatabase[hddDatabase["Model"].apply(str.upper).str.contains(split.upper() + " " + model[count + 1].upper())]
                    try:
                        self.hardware['HDDs'] = pd.concat([self.hardware['HDDs'], hddRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                count +=1
            count = 0
            fails = 0
            for split in model:
                if len(model) <= 2:
                    ssdRes = ssdDatabase[ssdDatabase["Model"].apply(str.upper).str.contains(split.upper())]
                    try:
                        self.hardware['SSDs'] = pd.concat([self.hardware['SSDs'], ssdRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                if count % 2 == 0 and len(model) > 2:
                    ssdRes = ssdDatabase[ssdDatabase["Model"].apply(str.upper).str.contains(split.upper() + " " + model[count + 1].upper())]
                    try:
                        self.hardware['SSDs'] = pd.concat([ self.hardware['SSDs'],ssdRes.iloc[0]])

                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                count +=1

        count = 0
        fails = 0
        for cpu in self.diagDict['Processor']:
            if cpu == '':
                break
            model = cpu.split(" ")
            for splitter in model:
                if len(model) <= 2:
                    cpuRes = cpuDatabase[cpuDatabase["Model"].apply(str.upper).str.contains(splitter.upper())]
                    try:
                        self.hardware['CPUs'] = pd.concat([self.hardware['CPUs'], cpuRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                if count % 2 == 0 and len(model) > 2:
                    if "(" in splitter or model[count + 1].upper():
                        stupidpanda = splitter.upper() + " " + model[count + 1].upper()
                    else:
                        stupidpanda = splitter.upper
                    print(stupidpanda)
                    try:
                        cpuRes = cpuDatabase[cpuDatabase["Model"].apply(str.upper).str.contains(stupidpanda)]
                        print(cpuRes.iloc[0])
                        self.hardware['CPUs'] = pd.concat([self.hardware['CPUs'], cpuRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                count +=1
        count = 0
        fails = 0
        for gpu in self.diagDict['Processor']:
            if cpu == '':
                break
            model = cpu.split(" ")
            for splitter in model:
                if len(model) <= 2:
                    cpuRes = cpuDatabase[cpuDatabase["Model"].apply(str.upper).str.contains(splitter.upper())]
                    try:
                        self.hardware['CPUs'] = pd.concat([self.hardware['CPUs'], cpuRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                if count % 2 == 0 and len(model) > 2:
                    if "(" in splitter or model[count + 1].upper():
                        stupidpanda = splitter.upper() + " " + model[count + 1].upper()
                    else:
                        stupidpanda = splitter.upper
                    print(stupidpanda)
                    try:
                        cpuRes = cpuDatabase[cpuDatabase["Model"].apply(str.upper).str.contains(stupidpanda)]
                        print(cpuRes.iloc[0])
                        self.hardware['CPUs'] = pd.concat([self.hardware['CPUs'], cpuRes.iloc[0]])
                    except Exception as e:
                        print("rip " + str(e))
                        fails +=1
                count +=1

        print(self.hardware)
        return





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    interpreter = DxDiagInterpreter("default")
    interpreter.is_out_of_date()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
