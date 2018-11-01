from operator import itemgetter
L = [[1, 2, 'd'], [3, 5, 'a'], [9, 7, 'b']]
P = sorted(L, key=itemgetter(2))
#L.sort(key=itemgetter(2))

line = [8,9,10]

L.sort(key=lambda line: line[2])
a = lambda line: line[len(L)-1]
L.sort(key=lambda line: line[len(L)-1])


sea_turtles_mdd.sort(key=lambda line: line[len(sea_turtles_mdd) - 1])

#sea_turtles_mdd.sort(key=lambda line: line[len(sea_turtles_mdd) - 1])
#talmid_mdd.sort(key=lambda line: line[len(talmid_mdd) - 1])
a=1