import pandas as pd
from flask import Flask, render_template, request, redirect, send_file
app = Flask(__name__)

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
            print(file1)
            file2 = request.files['file2']
            print(file2)

            if not allowed_extension(file1.filename) or not allowed_extension(file2.filename):
                print("At least one file extension is invalid. Please upload two .csv files!")
                return "At least one file extension is invalid. Please upload two .csv files!"

            def findDelimiter(file):
                result = pd.DataFrame()
                try:
                    result = pd.read_csv(file, sep='[:;,]', engine='python', encoding='UTF-8') # supported delimiters: : - ; - ,
                # except TypeError:
                #     print('type error: ', TypeError)
                # except IndexError:
                #     print('index error: ', IndexError)
                # except AttributeError:
                #     print('attritbute error: ', AttributeError)
                # except:
                #     print('unexpected error loading file')
                # return result
                except:
                    try: 
                       result = pd.read_csv(file, sep='[:;,]', engine='python', encoding='latin')
                    except:
                        print('File could not be read')
                return result

        table1 = findDelimiter(request.files['file1'])
        table2 = findDelimiter(request.files['file2'])

        writer = pd.ExcelWriter('Comparison.xlsx', engine='xlsxwriter')

        # run comparison table 1 vs table 2, find differences in entry values, and entries that are in table 1, but not table 2
        results = runComparison(True, table1, table2)
        df_comparison = results[0]
        saveToFile(df_comparison, 'Differences table 1 vs 2', writer)
        df_entrynotFound = results[1]
        saveToFile(df_entrynotFound, 'Entries not found in table 2', writer)

        # re-run with different compare mode: This time, the script will not look for differences in entry values again,
        # because that was done during the first run. It will only find entries that are in table 2 but not table 1
        df_entrynotFound = runComparison(False, table2, table1)[1]
        saveToFile(df_entrynotFound, 'Entries not found in table 1', writer)
        writer.save()

        # table1.to_csv('test', index=False)
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