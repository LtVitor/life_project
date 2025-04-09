from flask import Flask, request, render_template, redirect
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = 'dados_rotina.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = {
        'data_envio': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'acordou': request.form['acordou'],
        'soneca1': request.form['soneca1'],
        'soneca2': request.form['soneca2'],
        'almoco': request.form['almoco'],
        'jantar': request.form['jantar']
    }

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)