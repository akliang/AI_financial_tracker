
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

import csv
import tinydb
import tinydb.operations
import datetime

if len(sys.argv)==1:
  print "Needs an input file as an input parameter"
  exit()

infile=sys.argv[1]


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

  # remove spaces
  headers=[k.replace(' ','') for k in headers]

  db_handle = tinydb.TinyDB(db_name)
  db_handle.purge()
  for num,var in enumerate(line_items):
    # very special hack line for changing amount to float
    if (len(var)>2):
      var[4]=float(var[4])
    db_handle.insert(dict(zip(headers,var)))

  return db_handle


# set up categories
catdb = import_csv('./categories.csv','./categories.json','catdb')
mtdb  = import_csv(infile,'./moneytracker.json','mtdb')

# change the dollar amounts to float
# todo: find a db-friendly way to do this
# (currently done as a hack in import_csv)


# remove positive-value entries
mtdb.remove(tinydb.Query().amount > 0)

# scan for categories and report errors
for cat in catdb:
  # detect and record multiple-tagging
  for f in mtdb.search( (tinydb.Query().description.search(cat['item'])) & (tinydb.Query().tag.exists()) ):
    print "Double tag:     %-8s %-15s %-15s %s" % (f['amount'],f['tag'],cat['tag'],f['description'])
  mtdb.update(tinydb.operations.set('tag',cat['tag']),tinydb.Query().description.search(cat['item']))

for f in mtdb.search(~ tinydb.Query().tag.exists()):
  print "Untagged entry: %-40s %s" % (f['amount'],f['description'])


# build list of unique tags
uniqtags = set(f['tag'] for f in mtdb.search(tinydb.Query().tag.exists()))


#### output fun statistics ####

# todo: total spend, number of items, avg spend per item (also do this per category)
print "### overall statistics ###"
sumtot=0
for f in mtdb.all():
  sumtot+=f['amount']
print "Total amount spent:      %0.2f" % (sumtot)
print "Number of items:         %d"    % (len(mtdb))
print "Average amount per item: %0.2f" % (sumtot/len(mtdb))

# total sum per category
print ""
print "### spending by category ###"
for tag in uniqtags:
  sumtot = 0
  for f in mtdb.search(tinydb.Query().tag == tag):
    sumtot += f['amount']
  numf=mtdb.count(tinydb.Query().tag == tag)

  print "%-15s: %10.2f (number of items: %3d, avg spend per item: %10.2f)" % (tag,sumtot,numf,sumtot/numf)

# money spent per day
print ""
print "### spending by day ###"
day=[f['transdate'] for f in mtdb.all()]
for tag in set(sorted(day,key=lambda x: datetime.datetime.strptime(x,'%m/%d/%Y'))):
  sumtot = 0
  for f in mtdb.search(tinydb.Query().transdate == tag):
    sumtot += f['amount']

  print "%-15s: %0.2f" % (tag,sumtot)


# highest spend per category
print ""
print "### highest spending per category ###"
sumtot=0
for tag in uniqtags:
  min=0
  str=''
  for f in mtdb.search(tinydb.Query().tag == tag):
    if f['amount']<min:
      min=f['amount']
      str=f
  print "tag: %15s  item: %30s  amount: %0.2f" % (str['tag'],str['description'],str['amount'])
  sumtot+=str['amount']
print "%66s: %0.2f" % ("total",sumtot)


# list items over a certain threshold
threshold=-100
print ""
print "### items over %0.2f ###" % (threshold)
sumtot=0
for f in mtdb.search(tinydb.Query().tag.exists()):
  if (f['amount']<=threshold):
    print "tag: %15s  item: %30s  amount: %0.2f" % (f['tag'],f['description'],f['amount'])
    sumtot+=f['amount']
print "%66s: %0.2f" % ("total",sumtot)
    






