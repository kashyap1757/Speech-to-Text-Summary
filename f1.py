from flask import Flask, render_template, request
from text_summ import abs_summ
from flask_sqlalchemy import SQLAlchemy
#from flask_login import current_user  # Assuming you're using Flask-Login
import sqlite3
f1 = Flask(__name__)

@f1.route('/')
def index1():
    return render_template('index1.html')

@f1.route('/a', methods=['GET', 'POST'])
def a():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        summary, original_text, len_of_txt, len_of_smry = abs_summ(rawtext)
    return render_template('a.html', summary=summary, original_text=original_text, len_of_txt=len_of_txt, len_of_smry=len_of_smry)

if __name__ == "__main__":
    f1.run(debug=True, port=5001)
