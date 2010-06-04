import copy

municipalities = "sources/apygardos.txt"

# simply introducing an enumartion, so that we can use
# this as states when reading file.
# Probably might be a better way to do this in python
class State:
    # values here does not mean anything at all
    District = "d"
    County = "c"
    ElectionDistrict = "ec"
    Addresses = "ad"


# a DTO which is returned for eaach location read in the file
class MunicipalityLocation:
    District = ""
    County = ""
    ElectionDistrict = ""
    Addresses = ""

    # how to convert python object to string?
    # dont know yet, so using this hack :)
    # we could also iterate over all "fields??" in this object
    # but how to do that??
    def __str__(self):
        return "District: " + self.District + "\nCounty " + self.County + "\nElectionDistrict " + self.ElectionDistrict + "\nAddresses " + self.Addresses


def ConsumeNonEmptyLines(file, numberOfLines):
    for i in range(1, numberOfLines):
        notEmptyLine(file)

# a function which returns only non empty
# lines specific for Lithuanian municipality files.
def notEmptyLine(file):

    # read a line from file
    for s in file:

        # return each splitted line as separate line
        s = removeDumbCharacters(s)
        if (s == ""):
            continue
        return s

    return ""

def removeDumbCharacters(str):
    return str.strip("* \n")

def readAddress(file):
    strings = []
    # read first non empty line. This ensures that all blank lines are skipped
    strings.append(notEmptyLine(file))

    # read all non empty lines, and append to list
    # when empty strins is found, that means addresses are finished
    for s in file:
        s = removeDumbCharacters(s)
        if (s == ""):
            break;
        strings.append(s)

    return "".join(strings)



# a generator which returns a MunicipalityLocation object
# for each election district defined in the file
def getLocations(file):
    state = State.District
    location = MunicipalityLocation()
    while (1):
        line = notEmptyLine(file)

        if (line == ""):
            return

        if (line.find("apygarda") >=0 ):
            location.County = line
            state = State.ElectionDistrict
            continue

        if (line.find("apylinkė") >=0 ):
            location.ElectionDistrict = line
            state = State.Addresses

            # this county is special, since it has no streets.
            # So just instruct so skip reading streets for this county
            # HACK for now, but works
            # If you remove it, a test will fail
            if (line.find("Jūreivių rinkimų apylinkė") >=0 ):
                yield location
                state = State.County

            ConsumeNonEmptyLines(file, 2)
            continue

        if state == State.District:
            location.District = line
            state = State.County
            continue

        if (state == State.Addresses):
            location.Addresses = readAddress(file)
            state = State.District
            yield location;



"""
# debugging script, remove afterwards

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )
alytusRecordFile = scriptPath + "/tests/AlytausMiestas.txt"
print alytusRecordFile

def countNumberOfRecords(fileName):
        file = open(fileName, "r")
        count = 0
        for l in getLocations(file):
            print l.ElectionDistrict
            count += 1
        return count


print countNumberOfRecords(alytusRecordFile)
"""