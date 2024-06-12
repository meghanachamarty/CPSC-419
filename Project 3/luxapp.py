
#-----------------------------------------------------------------------
# luxapp.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

# application code!!
import json
from flask import Flask
from flask import request, make_response, redirect, url_for
from flask import render_template
from html import escape ## to thwart XSS attacks
from old_lux import main as old_lux

# Configure application
app = Flask(__name__, template_folder='.')

# Session(app)
# @app.route('/', methods=['GET'])
# @app.route('/index', methods=['GET'])
# def index():

#     html = ''
#     html += '<!DOCTYPE html>'
#     html += '<html>'
#     html += '<head>'
#     html += '<title>Lux</title>'
#     html += '</head>'

#     response = make_response(html)
#     return response

# @app.route("/")
# def hello_world():
#    return "<p>Hello, World!</p>"

# @app.route("/<name>")
# def hello(name):
#    return f"Hello, {escape(name)}!"


# creates the primary html webpage
@app.route('/', methods=['GET'])
def primary():

    error_msg = request.args.get('error_msg')
    if error_msg is None:
        error_msg = ''

    html = render_template('primary.html',
        error_msg=error_msg)
    response = make_response(html)
    return response

@app.route('/results', methods=['GET'])
def results():

    label = request.args.get('label')
    classifier = request.args.get('classifier')
    agent = request.args.get('agent')
    date = request.args.get('date')
    input_list = [classifier, date, agent, label]
    print(input_list)
 #   if (author is None) or (author.strip() == ''):
 #       error_msg = 'Please type an author name.'
 #      return redirect(url_for('search_form', error_msg=error_msg))

    # results_table should return a table object of the results we want output. I think
    # this takes in the right input but i have to go through more closely to see if this 
    # is what needs to be run to get the results we want
    results_table = old_lux(input_list)  # Exception handling omitted 
    json_table = json.dumps(results_table)

    # lines = results_table.headers()
    # for row in results_table:
    #     lines.extend(row)

    # lines = "\n".join(lines) # lines should be the new json object... but currently it breaks the program if i do that

    #convert table into dictionary, or list
    # rows of lists, list of lists
    # iterate over rows, split into lists or make into dict. key - columns, value is value for column
    # jinja to deconstruct json, use python table element to produce a table on the html 
    html = render_template('results.html', json_table=json_table)
    return html