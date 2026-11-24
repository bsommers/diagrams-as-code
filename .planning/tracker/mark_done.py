import json,sys
p='agents.json';d=json.load(open(p))
for a in d['agents']:
    if a['name'] in sys.argv[1:]: a['status']='done'
json.dump(d,open(p,'w'),indent=1)
