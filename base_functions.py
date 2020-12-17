
def import_csv(file, db_name, purge=False):
    debug = True

    with open(file, 'rt') as f:
        reader = csv.reader(f)
        line_items = list(reader)

    # first row is the header
    headers = line_items[0]
    del line_items[0]

    # convert everything to lower case
    headers = [k.lower() for k in headers]
    line_items = [[k.lower() for k in i] for i in line_items]

    # remove spaces in header
    headers = [k.replace(' ', '') for k in headers]

    db_handle = tinydb.TinyDB(db_name)
    if purge:
        db_handle.truncate()

    is_data = False
    if len(line_items[0]) > 2:
        is_data = True
        headers.append('hash')

    ins_cnt = 0
    skip_cnt = 0
    for var in line_items:
        if is_data:
            # this means the csv file is data, not the categories file
            # do some special operations

            # generate a hash string
            hashstr = ''.join(var)
            hashstr = hashlib.sha256(hashstr.encode('utf-8')).hexdigest()

            # convert the dollar value to float
            var[4] = float(var[4])

            # check if already in database
            if len(db_handle) > 0:
                if db_handle.count(tinydb.Query().hash == hashstr) > 0:
                    skip_cnt += 1
                    if debug:
                        for err in db_handle.search(tinydb.Query().hash == hashstr):
                            print(err)
                    continue

            # append hash to var
            var.append(hashstr)

        db_handle.insert(dict(zip(headers, var)))
        ins_cnt += 1

    print("Number of records inserted: %d" % ins_cnt)
    print("Number of records skipped: %d\n" % skip_cnt)

    return db_handle
# end import_csv


def save_csv(input_list, outfile):
    with open(outfile, 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerows(input_list)
# end save_csv


def plot_py(input_csv, *args):
    fig = plotly.subplots.make_subplots(rows=len(args)+1, cols=1)

    # read the input as a 2D list
    with open(input_csv, 'rt') as f:
        reader = csv.reader(f)
        line_items = list(reader)
    trace1 = go.Scatter(x=[item[0] for item in line_items], y=[item[1] for item in line_items])
    fig.append_trace(trace1, 1, 1)

    for argi, arg in enumerate(args):
        with open(arg, 'rt') as f:
            reader = csv.reader(f)
            line_items = list(reader)
        trace2 = go.Scatter(x=[item[0] for item in line_items], y=[item[1] for item in line_items])
        fig.append_trace(trace2, argi+2, 1)

    plotly.offline.plot(fig)
# end plot_py
