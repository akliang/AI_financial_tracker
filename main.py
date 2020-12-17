
import sys
import tinydb
import tinydb.operations
import datetime
import operator
import base_functions as bf


def main():
    if len(sys.argv)==1:
        print("Needs an input file as an input parameter")
        exit()

    print("\n\n### Script output and debug information ###")

    # set up categories
    print("Setting up categories...")
    catdb = bf.import_csv('./data/categories.csv', 'catdb', True)

    # import each in ut file
    for f in (sys.argv[1:]):
        print("Reading in file %s..." % f)
        mtdb = bf.import_csv(f, './moneytracker.json', 'mtdb')

    # change the dollar amounts to float
    # todo: find a db-friendly way to do this
    # (currently done as a hack in import_csv)

    # remove positive-value entries (those correspond to paying off a balance)
    mtdb.remove(tinydb.Query().amount > 0)

    # assign categories to each item and report errors
    for cat in catdb:
        # detect and record multiple-tagging
        for f in mtdb.search( (tinydb.Query().description.search(cat['item'])) & (tinydb.Query().tag.exists()) ):
            if f['tag']!=cat['tag']:  # truly a clash, not just an old entry
                print("Double tag:     %-8s %-15s %-15s %s" % (f['amount'],f['tag'],cat['tag'],f['description']))
        # add category tag to all entries that dont already have a tag assigned
        mtdb.update(tinydb.operations.set('tag',cat['tag']), (tinydb.Query().description.search(cat['item'])) & ~(tinydb.Query().tag.exists()) )
    for f in mtdb.search(~ tinydb.Query().tag.exists()):
        print("Untagged entry: %-40s %s" % (f['amount'],f['description']))

    print_output(mtdb)
# end main


def print_output(mtdb):
    # build uniqe list of tags used in db
    uniqtags = set(f['tag'] for f in mtdb.search(tinydb.Query().tag.exists()))

    # build list of dates
    uniqdays=[f['transdate'] for f in mtdb.all()]
    uniqdays=set(uniqdays)  # get unique values
    uniqdays=list(uniqdays)  # convert it back into list, because order matters
    uniqdays=sorted(uniqdays,key=lambda x:datetime.datetime.strptime(x,'%m/%d/%Y'))

    # output fun statistics
    print('\n'*2)

    print("### overall statistics ###")
    resrow = []
    sumtot = 0
    for f in mtdb.all():
        sumtot += f['amount']
    # round sumtot to nearest cent
    sumtot = "%0.2f" % sumtot
    sumtot = float(sumtot)
    resrow.append(['Total amount spent', sumtot])
    resrow.append(['Number of items', len(mtdb)])
    resrow.append(['Average amount per item', "%0.2f" % (sumtot/len(mtdb))])
    resrow.append(['Start date', uniqdays[0]])
    resrow.append(['End date', uniqdays[-1]])
    for f in resrow:
        print("%-30s: %10s" % (f[0], f[1]))
    bf.save_csv(resrow, "overview.csv")

    # total sum per category
    print("")
    print("### spending by category ###")
    resrow = []
    for tag in uniqtags:
        sumtot = 0
        for f in mtdb.search(tinydb.Query().tag == tag):
            sumtot += f['amount']
        numf=mtdb.count(tinydb.Query().tag == tag)
        resrow.append([tag, sumtot, numf, sumtot/numf])
    # sort by sumtot
    for f in sorted(resrow, key=operator.itemgetter(1)):
        print("%-15s: %10.2f (number of items: %3d, avg spend per item: %10.2f)" % (f[0], f[1], f[2], f[3]))
    bf.save_csv(resrow, "spending_per_category.csv")

    # money spent per day
    plusfac = -50
    print("")
    print("### spending by day ###")
    resrow = []
    for tag in uniqdays:
        sumtot = 0
        for f in mtdb.search(tinydb.Query().transdate == tag):
            sumtot += f['amount']
        resrow.append([tag,sumtot])

    for f in resrow:
        sys.stdout.write("%-10s: %8.2f   " % (f[0], f[1]))
        sys.stdout.flush()
        print("+"*(int(f[1]/plusfac)))
    bf.save_csv(resrow, "spending_per_day.csv")

    # highest spend per category
    print("")
    print("### highest spending per category ###")
    resrow = []
    sumtot = 0
    for tag in uniqtags:
        min = 0
        str = ''
        for f in mtdb.search(tinydb.Query().tag == tag):
            if f['amount'] < min:
                min = f['amount']
                str = f
        resrow.append([str['tag'], str['description'], str['amount']])
        sumtot += str['amount']
    print("%-15s %-30s %s" % ("==tag==", "==description==", "==amount=="))
    for f in sorted(resrow, key=operator.itemgetter(2)):
        print("%-15s %-30s %8.2f" % (f[0], f[1], f[2]))
    print("%-46s %8.2f" % ("--- total ---", sumtot))
    bf.save_csv(resrow, "highest_spend_per_category.csv")

    # list items over a certain threshold
    threshold = -100
    print("")
    print("### items over %0.2f ###" % threshold)
    resrow = []
    sumtot = 0
    for f in mtdb.search(tinydb.Query().tag.exists()):
        if (f['amount'] <= threshold):
            resrow.append([f['tag'], f['description'], f['amount']])
            sumtot += f['amount']
    print("%-15s %-30s %s" % ("==tag==", "==description==", "==amount=="))
    for f in sorted(resrow, key=operator.itemgetter(2)):
        print("%-15s %-30s %8.2f" % (f[0], f[1], f[2]))
    print("%-46s %8.2f" % ("--- total ---", sumtot))
    bf.save_csv(resrow,"items_over_spend_threshold.csv")
    bf.plot_py("spending_per_category.csv", "spending_per_day.csv", "highest_spend_per_category.csv", "items_over_spend_threshold.csv")
# end print_output


if __name__ == "__main__":
    main()
