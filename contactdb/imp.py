
municipalities = "sources/apygardos.txt"
a = "sources/a.txt"

class State:
    District = "d"
    County = "c"
    ElectionDistrict = "ec"
    
class MunicipalityLocation:
    def __init__(self):
        self._district = ""
    
    @property
    def District(self):
        return self._x;

    @District.setter
    def District(self, value):
        self._district = value
        


# a generator function which returns only non empty
# lines specific for Lithuanian municipality files.
def notEmptyLines(file):
    # read a line from file
    for line in file:
        # for some reason, lines in a file are separated by \r
        # so split by \r, 
        lines = line.split('\r')
        # return each splitted line as separate line
        for s in lines:
            s = s.strip("* ")
            yield s


    
def myF(file):
    state = State.District
    infile = open(file, "r")

    for line in notEmptyLines(infile):

        print line
        if state == State.District:
            districtName = line
            state = State.County
            print "district " + districtName
            continue

        if (state == State.County):
            countyName = line
            state = State.ElectionDistrict
            print line
            
        
    
