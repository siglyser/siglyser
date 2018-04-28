from flask import Flask, render_template, request
import pandas as pd

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
        df = pd.read_csv(request.files.get("filedata"))
        print(df)
        return render_template("sigsolver.html")
		
if __name__=="__main__":
    app.run(debug=True)

