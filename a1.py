from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def a2():
    transcribed_text = "This is the transcribed text from speech-to-text."
    return render_template('a2.html', transcribed_text=transcribed_text)

if __name__ == '__main__':
    app.run(debug=True)
