import copy

municipalities = "sources/apygardos.txt"
a = "sources/a.txt"

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
    def toString(self):
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

        if state == State.District:
            location.District = line
            state = State.County
            continue

        if (state == State.County):
            location.County = line
            state = State.ElectionDistrict
            continue

        if (state == State.ElectionDistrict):
            location.ElectionDistrict = line
            state = State.Addresses
            ConsumeNonEmptyLines(file, 3)

        if (state == State.Addresses):
            location.Addresses = readAddress(file)
            state = State.District

        yield location;


file = open(a, "r")
for loc in getLocations(file):
    print loc.toString()
