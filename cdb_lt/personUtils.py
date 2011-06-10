
def splitIntoNameAndSurname(fullName):
    spl = fullName.split(u" ")
    if len(spl) > 1:
        name = spl[0].strip(u".")
        surname = u" ".join(spl[1:])
        return name, surname.strip()
    spl = fullName.split(u".")
    return spl[0].strip(u"."), spl[1]
