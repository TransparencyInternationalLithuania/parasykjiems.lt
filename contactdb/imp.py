
municipalities = "sources/apygardos.txt"

class State:
    District = "d"
    County = "c"
    ElectionDistrict = "ec"
    


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
            if (s == ""):
                continue
            yield s
    
def myF(file):
    state = State.District
    infile = open(file, "r")

    for line in notEmptyLines(infile):
    
        if state == State.District:
            districtName = line
            state = State.County
            pass

        if (state == State.County):
            countyName = line
            state = State.ElectionDistrict
            print line
            
        
    
