import sqlite3
from flask import Flask, g, render_template_string, request
#from . import config


app = Flask(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE_NAME'])
    #return sqlite3.connect(config.DATABASE_NAME)


@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/home', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def home():
    # Save request data in the DB
    query = 'INSERT INTO request ("url", "method") VALUES (:url, :method);'
    params = {'url': request.url, 'method': request.method}
    # Insert your code here.
    # get the URL and the method and store it in the Database
    try:
        g.db.execute(query, params)
        g.db.commit()
    except sqlite3.IntegrityError:
        return 'Error with DB', 400
    return 'Success', 200


@app.route('/dashboard')
def dashboard():
    # Fetch all requests from the DB
    #query = 'SELECT url, method FROM request;'
    cursor = g.db.execute('SELECT url, method FROM request;')
    requests = [dict(url=row[0], method=row[1]) for row in cursor.fetchall()]

    # Calculate total requests
    total_requests = len(requests)

    # Calculate total requests per method
    request_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    total_per_method = {}
    for method in request_methods:
        total_per_method[method] = len([
            request for request in requests if request['method'] == method.upper()])

    base_html = """
        <html>
            <h1>Total requests: {{total_requests}}</h1>
            <h3>GET requests: {{total_per_method['GET']}}</h3>
            <h3>POST requests: {{total_per_method['POST']}}</h3>
            <h3>PUT requests: {{total_per_method['PUT']}}</h3>
            <h3>PATCH requests: {{total_per_method['PATCH']}}</h3>
            <h3>DELETE requests: {{total_per_method['DELETE']}}</h3>
        </html>
    """
    # build these dictionaries out of the data retrieved from the database
    '''
    total_requests = -1
    total_per_method = {
        'GET': -1,
        'POST': -1,
        'PUT': -1,
        'PATCH': -1,
        'DELETE': -1,
    }
    '''

    return render_template_string(
        base_html,
        total_requests=total_requests,
        total_per_method=total_per_method
    )
