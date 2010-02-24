import sys, pstats

if len(sys.argv) < 2:
    print "usage: python showprof.py filename [lines]"
    quit()

p = pstats.Stats(sys.argv[1])

if len(sys.argv) > 2:
    limit = int(sys.argv[2])
else:
    limit = 40

p.strip_dirs().sort_stats('cumulative').print_stats(limit)
