
from __future__ import division
# python3 division can handle int/int=float, whereas python2 returns an int


import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')


import csv
import tinydb
import tinydb.operations
import datetime
import operator

def main():
  if len(sys.argv)==1:
    print "Needs an input file as an input parameter"
    exit()

  # print some newlines to look prettier
  print '\n'*2
  print "### Script output and debug information ###"


  # set up categories
  catdb = import_csv('./categories.csv','./categories.json','catdb',True)

  # import each input file
  for d,f in enumerate(sys.argv[1:]):
    if d==0:
      purge=True
    else:
      purge=False
    print "Reading in file %s..." % f
    mtdb  = import_csv(f,'./moneytracker.json','mtdb',purge)

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
  print '\n'*2

  print "### overall statistics ###"
  sumtot=0
  for f in mtdb.all():
    sumtot+=f['amount']
  print "Total amount spent:      %0.2f" % (sumtot)
  print "Number of items:         %d"    % (len(mtdb))
  print "Average amount per item: %0.2f" % (sumtot/len(mtdb))

  # todo: sort by total amount
  # total sum per category
  print ""
  print "### spending by category ###"
  resrow=[]
  for tag in uniqtags:
    sumtot = 0
    for f in mtdb.search(tinydb.Query().tag == tag):
      sumtot += f['amount']
    numf=mtdb.count(tinydb.Query().tag == tag)
    resrow.append([tag,sumtot,numf,sumtot/numf])
  # sort by sumtot
  for f in sorted(resrow, key=operator.itemgetter(1)):
    print "%-15s: %10.2f (number of items: %3d, avg spend per item: %10.2f)" % (f[0],f[1],f[2],f[3])

  # money spent per day
  plusfac=-50
  print ""
  print "### spending by day ###"
  day=[f['transdate'] for f in mtdb.all()]
  day=set(day)  # get unique values
  day=list(day)  # convert it back into list, because order matters
  day=sorted(day,key=lambda x:datetime.datetime.strptime(x,'%m/%d/%Y'))
  for tag in day:
    sumtot = 0
    for f in mtdb.search(tinydb.Query().transdate == tag):
      sumtot += f['amount']

    sys.stdout.write("%-10s: %8.2f   " % (tag,sumtot))
    sys.stdout.flush()
    print "+"*(int(sumtot/plusfac))

  # highest spend per category
  print ""
  print "### highest spending per category ###"
  resrow=[]
  sumtot=0
  for tag in uniqtags:
    min=0
    str=''
    for f in mtdb.search(tinydb.Query().tag == tag):
      if f['amount']<min:
        min=f['amount']
        str=f
    #print "tag: %15s  item: %30s  amount: %0.2f" % (str['tag'],str['description'],str['amount'])
    resrow.append([str['tag'],str['description'],str['amount']])
    sumtot+=str['amount']
  print "%-15s %-30s %s" % ("==tag==","==description==","==amount==")
  for f in sorted(resrow, key=operator.itemgetter(2)):
    print "%-15s %-30s %8.2f" % (f[0],f[1],f[2])
  print "%-46s %8.2f" % ("--- total ---",sumtot)

  # list items over a certain threshold
  threshold=-100
  print ""
  print "### items over %0.2f ###" % (threshold)
  resrow=[]
  sumtot=0
  for f in mtdb.search(tinydb.Query().tag.exists()):
    if (f['amount']<=threshold):
      resrow.append([f['tag'],f['description'],f['amount']])
      #print "tag: %15s  item: %30s  amount: %0.2f" % (f['tag'],f['description'],f['amount'])
      sumtot+=f['amount']
  print "%-15s %-30s %s" % ("==tag==","==description==","==amount==")
  for f in sorted(resrow, key=operator.itemgetter(2)):
    print "%-15s %-30s %8.2f" % (f[0],f[1],f[2])
  print "%-46s %8.2f" % ("--- total ---",sumtot)
# end main



def import_csv(file,db_name,db_handle,purge = False):
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
  if purge==True:
    db_handle.purge()
  for num,var in enumerate(line_items):
    # very special hack line for changing amount to float
    if (len(var)>2):
      var[4]=float(var[4])
    db_handle.insert(dict(zip(headers,var)))

  return db_handle
# end import_csv


if __name__ == "__main__":
  main()

