from flask import Flask, render_template, request
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.resources import CDN
	
	
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/start')
def start():
    return render_template("start.html")
	
@app.route('/about')
def about():
    return render_template("about.html")

@app.route("/sigsolver", methods = ['GET', 'POST'])
def sigsolver():
    if request.method=='POST':
        temp1=request.files['filedata']
        print(temp1)
        #df = pd.DataFrame()
        df = pd.read_csv(request.files.get("filedata"), header=None, dtype = float)
        #print(df[0])
        #print(df[1])		
        p=figure(width=1000, height=300)
        p.title.text="Raw Data"
        p.line(df[0],df[1])
        script1, div1 = components(p)
        cdn_js=CDN.js_files[0]
        cdn_css=CDN.css_files[0]
        return render_template("sigsolver.html", script1=script1, div1=div1, cdn_css=cdn_css, cdn_js=cdn_js)


if __name__=="__main__":
    app.run(debug=True)

