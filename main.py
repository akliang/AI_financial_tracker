
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

import csv
from tinydb import TinyDB,where,Query
from tinydb.operations import add,set


def import_csv(file,db_name,db_handle):
  with open(file,'rb') as f:
    reader = csv.reader(f)
    line_items = list(reader)

  # first row is the header
  headers=line_items[0]
  del line_items[0]

  # convert everything to lower case
  headers=[k.lower() for k in headers]
  line_items=[[k.lower() for k in i] for i in line_items]

  db_handle = TinyDB(db_name)
  db_handle.purge()
  for num,var in enumerate(line_items):
    # very special hack line for changing amount to float
    if (len(var)>2):
      var[4]=float(var[4])
    db_handle.insert(dict(zip(headers,var)))

  return db_handle


# set up categories
catdb = import_csv('./categories.csv','./categories.json','catdb')
mtdb  = import_csv('./full.csv','./moneytracker.json','mtdb')

# change the dollar amounts to float
# todo: find a db-friendly way to do this
# (currently done as a hack in import_csv)


# remove positive-value entries
mtdb.remove(Query().amount > 0)

# scan for categories and report errors
for cat in catdb:
  # detect and record multiple-tagging
  for f in mtdb.search( (Query().description.search(cat['item'])) & (Query().tag.exists()) ):
    print "Double tag:     %-8s %-15s %-15s %s" % (f['amount'],f['tag'],cat['tag'],f['description'])
  mtdb.update(set('tag',cat['tag']),Query().description.search(cat['item']))

for f in mtdb.search(~ Query().tag.exists()):
  print "Untagged entry: %-40s %s" % (f['amount'],f['description'])


# build list of unique tags
#uniqtag = set()
#for f in mtdb.search(Query().tag.exists()):
#  uniqtag.add(f['tag'])

#print uniqtag
uniquetag = set(f['tag'] for f in mtdb.search(Query().tag.exists()))





exit()



#### output fun statistics ####

# total sum per category
for cat in catdb:
  sumtot = 0
  for f in mtdb.search(Query().tag == cat['tag']):
    sumtot += f['amount']

  print "%-15s: %0.2f" % (cat['tag'],sumtot)



