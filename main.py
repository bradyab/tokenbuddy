from flask import Flask, jsonify, request, render_template, url_for,redirect, Response
import random
import pandas as pd
import os
import ipdb
from datetime import datetime 
import numpy as np
from werkzeug.utils import secure_filename # pip install werkzeug==2.0.3
from process import process


app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)
    
@app.route('/')
def form():
    return render_template('form.html')
    
@app.route('/upload', methods = ['POST', 'GET']) 
def upload():
    if request.method == 'POST':
        uploaded_filenames = []

        # download files from user and save filenames
        for f in request.files.getlist('my_file[]'):
            f.save(os.path.join("uploads/", f.filename))
            uploaded_filenames.append("uploads/" + f.filename)

        # check to see which files were uploaded
        expected_names = ['uploads/orders.csv', 'uploads/deposits.txt', 'uploads/withdrawals.txt', 'uploads/system_deposits.txt']
        existing_names = []
        for n in range(4):
            name_exists = expected_names[n] if expected_names[n] in uploaded_filenames else None
            existing_names.append(name_exists)

        if all(element == None for element in existing_names):
             return "no files were found. are the filenames correct?" 

        # this is where the magic happens
        results = process(existing_names[0], existing_names[1], existing_names[2], existing_names[3])
        results.to_csv('output.csv', index=False)
        
        # remove all uploaded files
        for f in os.listdir("uploads/"):
            os.remove(os.path.join("uploads/", f))

        return render_template('download.html')

@app.route("/download")
def download():
    with open("output.csv") as fp:
        csv = fp.read()
        os.remove("output.csv")
    
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=output.csv"})
        

if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000),  # Randomly select the port the machine hosts on.
    debug=True
	)