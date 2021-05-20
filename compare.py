import pandas as pd
import numpy as np

#IMPROVEMENTS & TO DO
# add file extension check for CSV format
# investigate: differentiate between/allow for different delimiters?
# optional: include part of actual file name from the files that user is uploading to names of saved files

#the comparison requires comparing table1 against table2 and vice versa in order to find values that are in one table, but not the other.
#therefore, the files are imported based on current comparison mode, and in mode 2to1, their order is switched

# to avoid diff. based on data format: convert numbers to equal format/"syntax", then to string
def toString(x):
        print('from ', x, type(x))
        if type(x) == str:
            return x
        if type(x) == np.float64 or type(x) == np.int64:
            x.tolist()
        x = str(float(x))
        if x[-1] == '0':
            x = x[0:-2] #removing .0 from the float
        print('to ', x, type(x))
        return str(x)

#---Comparison funct-----------------------------------------------------------------------------
def runComparison(comparer, df1, df2):

    df_comparison = pd.DataFrame() #tables have to be initalized because they are later referred to for concatenation
    df_entrynotFound = pd.DataFrame()

    # in both tables, the first column must be the one that contains the entries' ID/key
    keyCol = df2.iloc[:,0] # 1st column in the table we're comparing to
    keyColArray = list(map(toString, keyCol.values)) # converting entries to string for comparison
    # print('to str: ', test, pd.Series(keyColArray))
    keyCol = pd.Series(keyColArray)

    #---compare rows funct------------------------------------
    def compareRows(rowA):

        key = toString(rowA[0]) #saving the key value from 1st table so I can get corresponding value from 2nd table
        deviations = pd.DataFrame() #here's where I'll store the info on deviating entries
        
        #now going through every col entry in rowA
        for category, value in rowA.items():

            if category not in df2.columns: #if category(column) does not exist in table 2, ignore & break
                break
            
            valueBList = pd.Series(df2[category].where(keyCol == key).values) #identifiying value for same ID/col in table2 > array with comparison resut for each row
            valueB = list(filter(lambda x: pd.isna(x) == False, valueBList)) #from results array, filtering out only those values that are not 'NaN'
            
            if (pd.isna(valueBList.values)).all(): #if the result contains only NaN values > cell is empty:
                    if(pd.isna(value) or value == float('nan')): #see if corresponding value in rowA is NaN, too, in which case don't list as difference
                        break
                    else: #if corresponding value in rowA is not NAN, redefine valueB so its not an empty array
                        valueB = [float('nan')]          

            value = toString(value)
            valueB[0] = toString(valueB[0])

            print(value, valueB[0])

            if value != valueB[0]: #now actually comparing value of key/colName in table1 vs same key/colName in table2
                
                #print('deviating value: ', valueB[0])
                #print(f'Difference found in entry with ID {key}, in category: {category}') #optional: log the info
                newRow = [[key, category, value, str(valueB[0])]]
                #print(newRow) #activate when debugging
                add = pd.DataFrame(newRow, columns=['Entry ID in table 1', 'Difference found in', 'Value in table 1', 'Value in table 2'])
                deviations = pd.concat([deviations, add])

        return deviations
    #--------------------------------end of compare rows funct----------------------------------

    for currentRow, values in df1.iterrows(): # going through each row in table 1
        
        rowDf1 = pd.Series(df1.iloc[currentRow]) # grab values from current row of table 1, save as Series
        key = toString(rowDf1.values[0]) # set entry in 1st column as key to look for in table 2
        
        # now, look for this key in table 2. If it is not found, add to "not found" sheet for final results file
        if df2.loc[keyCol == key].empty :
            newRow =[[key, rowDf1.index[1], rowDf1.values[1]]]
            result = pd.DataFrame(newRow, columns=['Key not found in table 2', 'name next col table 1', 'value next col table 1'])
            df_entrynotFound = pd.concat([df_entrynotFound, result]) #add result to compare df
            #print(f'ID no. {key} not found in table 2') #optional: log the info
        
        # if it is found: identify differences and store them in table for for final results file, except for comparison mode '2to1'
        # where differences have already been found + listed and we are only interested in entries that are in table2 but not table1.
        if df2.loc[keyCol == key].empty == False and comparer != '2to1':
            result = compareRows(rowDf1) #pass rowDf1 to compare funct to compare it to corresponding row in table2       
            df_comparison = pd.concat([df_comparison, result])
            #print(result)

    return [df_comparison, df_entrynotFound]
#---End of comparison funct-----------------------------------------------------------------------------

# save results as CSV files, as well as different sheets in same Excel file. Use excel format and writer for that. Index not included in files

#writer = pd.ExcelWriter('Tables_compare.xlsx', engine='xlsxwriter')
def saveToFile(data, name, writer):
    data.to_excel(writer, sheet_name=str(name), index=False)
    # data.to_csv(str(name), index=False)

# results = runComparison(comparer)
# df_comparison = results[0]
# saveToFile(df_comparison, 'Differences table 1 vs 2')
# df_entrynotFound = results[1]
# saveToFile(df_entrynotFound, 'Entries not found in table '+comparer[-1])

# comparer = '2to1'

# df_entrynotFound = runComparison(comparer)[1]
# saveToFile(df_entrynotFound, 'Entries not found in table '+comparer[-1])
# writer.save()