def ExtractRange(args):
    fromNumber = 0
    toNumber = None
    parts = args.strip("[]").split(":")
    if (len(parts) >= 1):
        if (parts[0].strip() != u""):
            fromNumber = int(parts[0])
    if (len(parts) >= 2):
        if (parts[1].strip() != u""):
            toNumber = int(parts[1])
    return fromNumber, toNumber