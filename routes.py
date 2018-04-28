from flask import Flask, render_template, request
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.resources import CDN
import numpy as np
from scipy.fftpack import fft
from scipy.signal import butter, lfilter
	
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
        df_np = np.transpose(df.values)
        freq_hz, fft_vibr, fs = evalfreqfftvect(df_np[0], df_np[1])
        p2 = figure(width=1000, height=300)
        p2.title.text="FFT"
        p2.line(freq_hz, fft_vibr)
        script2, div2 = components(p2)
		
        cdn_js=CDN.js_files[0]
        cdn_css=CDN.css_files[0]
        return render_template("sigsolver.html", script1=script1, div1=div1, script2 = script2, div2 = div2, cdn_css=cdn_css, cdn_js=cdn_js)


		
def evalfreqfftvect(time_sec, vibr):
    datalength_fft = len(time_sec)
    datalengthby2 = int(datalength_fft/2)
    timeavgcalc = np.array([], dtype = float)
    time_sec_i = np.delete(time_sec,len(time_sec)-1)
    time_sec_i_1 = np.delete(time_sec,0)
    timeavgcalc = time_sec_i_1 - time_sec_i
    sigint_avg = np.mean(timeavgcalc)
    siginf = 1/(datalength_fft*sigint_avg)
    freqhztemp = np.arange(0,datalength_fft,dtype = float)
    freqhz = freqhztemp*siginf
    freqhz = freqhz[0:datalengthby2]
    vibr_fft = np.abs(fft(vibr,axis = -1))
    vibr_fft = ((vibr_fft[0:datalengthby2])/datalength_fft)*2
    return freqhz,vibr_fft, max(freqhz)*2
	

if __name__=="__main__":
    app.run(debug=True)

