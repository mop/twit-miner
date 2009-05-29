import pstats

p = pstats.Stats('prof-output-users')
p.sort_stats('cumulative').print_stats()
