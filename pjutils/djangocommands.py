import management
import types

def ExecManagementCommand(commands):
    for i in commands:
        commandName = i
        commandArgs = {}
        if (isinstance(i, types.TupleType)):
            commandName = i[0]
            commandArgs = i[1]

        print "importing %s" % commandName
        management.call_command(name = commandName, **commandArgs)
  