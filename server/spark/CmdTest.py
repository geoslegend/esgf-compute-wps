# Run using 'MASTER=local[4] spark-submit ./latency_test.py'
# type 'run' at prompt.
#
# import cdutil, cdms2
from utilities import Profiler
import cmd

profiler = Profiler()
num_procs = 4

def compute( value ):
    return value * 2

def run_comp_test():
    return range(num_procs)

class CommandProcessor(cmd.Cmd):

    def do_run(self, line):
        profiler.mark()
        result = run_comp_test()
        profiler.mark("CompTest")
        profiler.dump( " Result = %s " % str( result ) )
        return False

    def do_EOF(self, line):
        return True


CommandProcessor().cmdloop()




