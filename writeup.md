# Writeup

1. Discuss your solution’s time complexity. What tradeoffs did you make?
    - To parse the CSV files and output results, we need at least to iterate over the entire CSVs this will be done in O(n) time complexity.
    - Throught the program execution we assumed the csv are all valid an there is no null data in it. Meaning, no sanitize were done on the data, nor verbose exception checks. Like: does the provided CSV file exists? Does all the provided CSVs files provides valid headers? Etc.
    - To ease readability, however increasing total time execution, some CSV were fetched more than one time. For example, in `_legislator_support_oppose` and `_analyze_bill_votes_and_sponsors` `vote_result.csv` is processed two times. We could have simplify this, by onling fetching it one time but at the cost of  readability and mantainability.
    - All the parsing and fetching could easily be done with `pandas` package. For example, a simple csv to dataframe method followed by `vote_counts = vote_results_df.groupby(['legislator_id', 'vote_type']).size()`. However, a personal choose was made to stick with methods and built-ins from Python.

2. How would you change your solution to account for future columns that might be requested, such as “Bill Voted On Date” or “Co-Sponsors”?
    - Assuming those two new columns would go to `vote_results.csv` file, we would be adding a new key to the result dictionary in returned by `_legislator_support_oppose`.

3. How would you change your solution if instead of receiving CSVs of data, you were given a list of legislators or bills that you should generate a CSV for?
    - We could change the `_parse_csv` function to create the CSSv files rather than parsing them from disk.

4. How long did you spend working on the assignment?
    - Approximately ~4hr.
