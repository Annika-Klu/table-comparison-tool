# Table comparison tool

## What is this  about?
Imagine you have different versions of a table/data file that you wish to compare. Perhaps a list that is maintained by more than one person or system, and you need to make sure your versions match. This is a cumbersome task when you have to solve it manually. But grieve no more, my handy tool is here!

## How does it work?
The script takes an entry's ID value from the first table, looks for it in the second table and sees if it can find it there.
If it doesn't, it will list this entry as an  entry that was found in table 1, but not in table 2. This will happen vice  versa for table 2 against table 1. Moreover, the script compares values of entries with the same ID, and if they are different, the script lists these differences.

## What does it require?
The table entries MUST have a unique identifier, or key value. For example, this could be an order number, or an employee number - but it could also be other characters, as long as it is unique to an entry.
This key value MUST be located in the first column of your table. The orders of the other columns, as well as the orders of the rows in general, is completely irrelevant.
you have a use case, too, I very much hope my tool will save you some time!

## Improvements on the to do list
- better & more user-friendly error handling
- optional settings user can make, e. g. whether tool should be case sensitive when identifying differences or not