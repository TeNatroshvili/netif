from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html')

if __name__ == '__main__':
    app.run(debug=1)