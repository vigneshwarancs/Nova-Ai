import os

from flask import Flask, render_template, request, redirect, url_for

app= Flask(__name__)

@app.route('/', methods=['GET'])
def index():
     a="Hello world"
     return a

if __name__ == '__main__':
    app.run(debug=True)
