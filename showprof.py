import sys, pstats

if len(sys.argv) != 2:
    print "usage: python showprof.py filename"
    quit()
p = pstats.Stats(sys.argv[1])
p.strip_dirs().sort_stats('cumulative').print_stats(40)
