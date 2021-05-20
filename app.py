import pandas as pd
from flask import Flask, render_template, request, redirect, send_file
app = Flask(__name__)

from compare import runComparison, saveToFile

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        table1 = pd.read_csv(request.files['file1'], delimiter=';')
        table2 = pd.read_csv(request.files['file2'], delimiter=';')

        if request.files['file1'] == None or request.files['file2'] == None:
            return 'Please upload 2 files!'

        #comparer = '1to2'
        writer = pd.ExcelWriter('Comparison.xlsx', engine='xlsxwriter')

        # run comparison
        results = runComparison('1to2', table1, table2)
        df_comparison = results[0]
        saveToFile(df_comparison, 'Differences table 1 vs 2', writer)
        df_entrynotFound = results[1]
        saveToFile(df_entrynotFound, 'Entries not found in table 2', writer)

        # re-run with different comparer
        #comparer = '2to1'
        df_entrynotFound = runComparison('2to1', table2, table1)[1]
        saveToFile(df_entrynotFound, 'Entries not found in table 1', writer)
        writer.save()

        # table1.to_csv('test', index=False)
        return redirect('/result')
            
        # if request.files:
        #     return 'you uploaded something'
        # else:
        #     return 'no files uploaded'
    return render_template('main.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        if request.form.get('button') == 'clicked':
            return send_file('Comparison.xlsx')
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)