import pandas
import sys
from uuid import uuid1

groups = {}
pgroups = {}
xcount = 0

def get_group(key):
    if key in groups:
        return groups[key]
    else:
        return None

data = pandas.read_csv(sys.argv[1], header=None)

for index, row in data.iterrows():
    a = row[0]
    b = row[1]
    ga = get_group(a)
    gb = get_group(b)
    if ga == None:
        if gb == None:
            uuid = uuid1()
            groups[a] = uuid
            groups[b] = uuid
            pgroups[uuid] = []
            pgroups[uuid].append(a)
            pgroups[uuid].append(b)
        else:
            groups[a] = gb
            pgroups[gb].append(a)   
    else:        
        if gb == None:
            groups[b] = ga
            pgroups[ga].append(b)   
        else:
            if ga != gb:
                xcount += 1
                print(ga,gb)
                print('\t',row)
            
for x in pgroups:
    print(x)
    for y in pgroups[x]:
        print('\t',y)

print("GROUP COUNT:", len(pgroups), "CONFLICTS:", xcount)
