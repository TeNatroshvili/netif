from flask import Flask, render_template, request
import json
import scrapy
from scrapyNetIF.scrapyNetIF.spiders.NetIF import postsomeThing
app = Flask(__name__)



@app.route('/setRateLimit',methods=['Get','POST'])
def set_rate_limit():
    print("requestdata")
    print(request.args)
    login_data={"password":"Syp2223"}
    form_data={"_submit":"Apply","R11":"2","R52":"on","R12":"2","R51":"1"}
    postsomeThing(form_data)
    return "done"
    

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/visualeditor')
def visualeditor():
    return render_template('visualeditor.html')

if __name__ == '__main__':
    app.run(debug=1)
