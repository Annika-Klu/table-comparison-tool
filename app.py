import pandas as pd
from flask import Flask, render_template, request, redirect, send_file
app = Flask(__name__)

import chardet
from compare import runComparison, saveToFile

app.config["ALLOWED_FILE_EXTENSIONS"] = ["CSV"]

def allowed_extension(filename):
    
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':

        if request.files:

            file1 = request.files['file1']
            file2 = request.files['file2']

            #shorten filename if necessary and store in variable
            def fileName(file):
                if len(file.filename) > 10:
                    return file.filename[:10] + '...'
                return file.filename

            file1Name = fileName(file1)
            file2Name = fileName(file2)

            if not allowed_extension(file1.filename) or not allowed_extension(file2.filename):
                return render_template('error.html', error = 'extension')

            # ---- DECODE, 1st ATTEMPT: trying different encoding formats with a loop --------
            
            # def decode(file):
            #     result = pd.DataFrame()
            #     print(file.filename)
 
            #     encoding = ['utf8', 'utf16', 'iso-8859-1', 'ascii', 'latin1', 'hz']
            #     for enc in encoding:
            #         try:
            #             result = pd.read_csv(file, sep='[:;,]', engine='python', encoding=enc)
            #             if not result.empty:
            #                 print('file decoded with: ', enc)
            #                 break
            #         except IndexError:
            #             print('Index error with enc format: ', enc)
            #             continue
            #         except UnicodeError:
            #             print('Unicode error with enc format: ', enc)
            #             continue
            #         except UnicodeDecodeError:
            #             print('Unicode decode error with enc format: ', enc)
            #             continue
            #         except:
            #             print('File could not be read with enc format: ', enc)
            #             continue
            #         finally:
            #             file.seek(0)
            #     return result

        # table1 = decode(file1)
        # table2 = decode(file2)

        #----- DECODE, 2nd attempt: using chardet module ------

        def decode(file):
                check = file.read()
                file.seek(0)
                detection = chardet.detect(check)
                charenc = detection['encoding']
                print(charenc)
                return charenc

        def define(file, fileName):
            try: 
                enc = decode(file)
                table = pd.read_csv(file, sep='[:;,]', engine='python', encoding=enc)
                return table
            except:
                return render_template('error.html', file = fileName, error = 'encoding')            
        
        table1 = define(file1, file1Name)
        table2 = define(file2, file2Name)

        #--------------------------------------------------------

        writer = pd.ExcelWriter('Comparison.xlsx', engine='xlsxwriter')

        # run comparison table 1 vs table 2, find differences in entry values, and entries that are in table 1, but not table 2
        results = runComparison(True, file1Name, file2Name, table1, table2)
        df_comparison = results[0]
        saveToFile(df_comparison, (file1Name + ' vs ' + file2Name), writer)
        df_entrynotFound = results[1]
        saveToFile(df_entrynotFound, ('Entries not in '+ file2Name), writer)

        # re-run in different compare mode: This time, the script will not look for differences in entry values again,
        # because that was done during the first run. It will only find entries that are in table 2 but not table 1
        df_entrynotFound = runComparison(False, file2Name, file1Name, table2, table1)[1]
        saveToFile(df_entrynotFound, ('Entries not in ' + file1Name), writer)
        writer.save()

        return redirect('/result')
            
    return render_template('main.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        if request.form.get('button') == 'clicked':
            return send_file('Comparison.xlsx')
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)