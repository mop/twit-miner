import pstats

p = pstats.Stats('prof-output')
p.sort_stats('cumulative').print_stats()
