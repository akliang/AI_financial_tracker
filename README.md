# moneytracker

Feed all your various financial data (bank accounts, credit card statements and stock portfolios) in a CSV format and this script automatically cleans and structures the raw CSV into a fixed database format.  Next, it tries to determine the category to assign to each row of the database (currently using string match) and then generates a pretty dashboard of your financial status and spending categories.

## Dependencies

1. tinydb
2. plotly

## Future plans

* Convert dashboard from Plotly to Tableau
* Upgrade from string match to hash look-up
* Far future: Instead of using hash look-up (which is semi-hard-coded), perform a Google search and try to use NLP to figure out what the category should be

