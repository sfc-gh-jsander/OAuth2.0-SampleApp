###################################################################
###################################################################
##        The MIT License - SPDX short identifier: MIT           ##
###################################################################
###################################################################
#
#Copyright 2019 @sanderiam & https://github.com/snowflakedb
#
#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without
#limitation the rights to use, copy, modify, merge, publish, distribute,
#sublicense, and/or sell copies of the Software, and to permit persons
#to whom the Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# Please consider this script an example.
# Do not use this in any production scenario

from bottle import Bottle, request, run, redirect, SimpleTemplate, template
from urllib.parse import urlparse, urlunparse, urlencode, quote
import urllib.request
import requests
import string
import random
import base64
import ssl
import json
import subprocess
from subprocess import STDOUT,PIPE
import snowflake.connector
import configparser
from PKCE import code_verifier, code_challenge

# define the bottle app that will wrap around all this 
app = Bottle()

# begin an instance of the INI reader
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

# import the coniguration from the ini file in this directory
# change to a full path if you move the file
config.read('OAuth2_0-SampleApp.ini')

# App settings
app_port = config['APP']['port']

# Snowflake OAuth settings
client_id = config['OAUTH']['client_id']
client_secret = config['OAUTH']['client_secret']
redirect_uri = config['OAUTH']['redirect_uri']
authorization_endpoint = config['OAUTH']['authorization_endpoint']
token_endpoint = config['OAUTH']['token_endpoint']
do_pkce = config['OAUTH']['do_pkce']

# External OAuth settings
extoauth_scope = config['EXTOAUTH']['extoauth_scope']
extoauth_oauth_client_id = config['EXTOAUTH']['extoauth_oauth_client_id']
extoauth_oauth_client_secret = config['EXTOAUTH']['extoauth_oauth_client_secret']
extoauth_token_endpoint = config['EXTOAUTH']['extoauth_token_endpoint']
extoauth_jws_key_endpoint = config['EXTOAUTH']['extoauth_jws_key_endpoint']
extoauth_issuer = config['EXTOAUTH']['extoauth_issuer']

# Java settings
java_class = config['JAVA']['compiled_classpath']
java_jdbcjar = config['JAVA']['snowflake_jdbc_classpath']

# Snowflake settings
snowflake_account = config['SNOWFLAKE']['account']
snowflake_accounturl = config['SNOWFLAKE']['accounturl']
snowflake_authenticator = config['SNOWFLAKE']['authenticator']
snowflake_role = config['SNOWFLAKE']['role']
snowflake_query = config['SNOWFLAKE']['query']

# if PKCE has been set to TRUE, generate the code verifier and challenge
# see https://tools.ietf.org/html/rfc7636 for details
if do_pkce == "TRUE":
    code_verifier = code_verifier()
    code_challenge = code_challenge(code_verifier)

# generate a string to use for the OAuth state to protect against CSRF
# see https://tools.ietf.org/id/draft-bradley-oauth-jwt-encoded-state-08.html
# for details
def string_num_generator(size):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

state_parameter = string_num_generator(150)

# this dict will maintain the state of the token throughout the run of the program
state = {}

# the index page for the application outputs a login prompt
@app.get('/')
def do_get():
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: do_get')
    code = request.query.get('code')
    if code:
        returned_state_parameter = request.query.get('state')
        # UNCOMMENT FOR DEBUGGING # print('DEBUGGING... setting returned_state_parameter to a bad value on purpose')
        # UNCOMMENT FOR DEBUGGING # returned_state_parameter = 'noway' # use to test inproper returns

        if returned_state_parameter != state_parameter:
            return template('bad.html', returned_state_parameter=returned_state_parameter, state_parameter=state_parameter)

        # got code from OAuth 2 authentication server
        token = get_token_code(code)
        state.update(token)
        return template('token.html', items=token.items(), refresh_token=urllib.parse.quote(token['refresh_token']))
        # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    else:
        return template('main.html')

# handles the forwarding for authentication used for Snowflake OAuth
@app.get('/logon')
def do_logon():
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: do_logon {Snowflake OAuth}')
    pr=list(urlparse(authorization_endpoint))
    # set query
    if do_pkce == "TRUE":
        pr[4]=urlencode({
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
	    'state': state_parameter,
	    'code_challenge': code_challenge,
	    'code_challenge_method': 'S256'
        })
    else:
        pr[4]=urlencode({
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
	    'state': state_parameter
        })
    # perform redirection to OAuth 2 authentication server
    # UNCOMMENT FOR DEBUGGING # print('pr for logon: {}'.format(pr))
    redirect(urlunparse(pr))

# handles the forwarding for authentication used for Snowflake OAuth
@app.get('/extoauth', method='POST')
def do_extoauth():
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: do_extoauth')

    # Resource owner (enduser) credentials for OAuth 2.0 Resource Owner Password Credentials (ROPC) grant
    RO_user = request.forms.get('username')
    RO_password = request.forms.get('password')

   # print (RO_user)
   # print (RO_password)

    data = {'grant_type': 'password', 'username': RO_user, 'password': RO_password, 'scope': extoauth_scope}

    access_token_response = requests.post(extoauth_token_endpoint, data=data, verify=False, allow_redirects=False, auth=(extoauth_oauth_client_id, extoauth_oauth_client_secret))

    # UNCOMMENT FOR DEBUGGING # print("response headers: ")
    # UNCOMMENT FOR DEBUGGING # print(access_token_response.headers)
    # UNCOMMENT FOR DEBUGGING # print("response data: " + access_token_response.text)

    tokens = json.loads(access_token_response.text)
    # UNCOMMENT FOR DEBUGGING # print("access token: " + tokens['access_token'])

    state.update(tokens)

    refresh = json.loads('{"refresh_token":"null"}')
    state.update(refresh)
    return template('token.html', items=state.items(), refresh_token='null')

# used to get the ROPC user's credentials doe External OAuth
@app.get('/logonform')
def do_logonform():
    return template('logonform.html')

# this will run the supplied SQL in the Python connector
@app.get('/getattr')
def get_attributes():
    print('ENTERING: get_attributes')
    print('state right now: {}'.format(state))

    cnx = snowflake.connector.connect(
        #account=snowflake_account,
        account="XXXXXXX",
        authenticator=snowflake_authenticator,
        role=snowflake_role,
        token=state['access_token'],
        warehouse="XXXXXX",
        database="XXXXX",
        schema="XXXX"
    )

    # Querying data
    cur = cnx.cursor()

    rowdict = {}

    try:
        cur.execute(snowflake_query)

        for (col1, col2) in cur:
            rowdict[col1] = col2
            print ("These are the results from PYTHON: "+str(rowdict))
    finally:
        cur.close()

    return template('attributes.html', results=rowdict.items(), items=state.items(), refresh_token=urllib.parse.quote(state['refresh_token']))

# this will run the supplied SQL in the JDBC connector
@app.get('/getattrjava')
def get_attrjava():
    print('ENTERING: get_attrjava')
    print('state right now: {}'.format(state))
    rowdict = {}

    # create the SQL to pass
    # javaSQL = "\"" + snowflake_query + "\""
    javaSQL = snowflake_query

    # create the classpath
    classpath = java_class + ":" + java_jdbcjar

    print("Classpath " + classpath + ", SQL " + javaSQL)

    result = subprocess.run(['java', '-cp', classpath, 'OAuthJDBCTest', state['access_token'], snowflake_accounturl, javaSQL, snowflake_role], stdout=subprocess.PIPE, universal_newlines=True, shell=False)

    print("This is the command result: ")
    print(result)
    print("The end of the command.")

    results = result.stdout.splitlines()

    print("these are the results from JAVA: ")
    print(results)
    print("The end of the resultset.")

    for line in results:
        if len(line) != 0:
            (a, b) = line.split(',')
            #(a, b) = line.decode().split(',')
            col1 = a.strip()
            col2 = b.strip()
            rowdict[col1] = col2

    return template('attributes.html', results=rowdict.items(), items=state.items(), refresh_token=urllib.parse.quote(state['refresh_token']))

# performs a refresh of the access token using the refresch token
@app.get('/refresh')
def do_refresh():
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: do_refresh')
    # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    token = refresh_access_token(request.query.get('refresh_token'))
    state.update(token)

    # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    return template('token.html', items=state.items(), refresh_token=urllib.parse.quote(state['refresh_token']))

def get_token_code(code):
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: get_token_code')
    # prepare POST parameters - encode them to urlencoded
    if do_pkce == "TRUE":
        data = urlencode({
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
	    'code_verifier': code_verifier
        })
    else:
        data = urlencode({
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        })
    data = data.encode('ascii')  # data should be bytes
    # UNCOMMENT FOR DEBUGGING # print('data for token req: {}'.format(data))
    resp_text = post_data(data, prepare_headers(), token_endpoint)

    # UNCOMMENT FOR DEBUGGING # print(resp_text)
    return json.loads(resp_text)

# helper functions for the code above
def refresh_access_token(refresh_token):
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: refresh_access_token')
    # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    # prepare POST parameters - encode them to urlencoded
    data = urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': redirect_uri
    })
    data = data.encode('ascii')  # data should be bytes
    resp_text = post_data(data, prepare_headers(), token_endpoint)

    # UNCOMMENT FOR DEBUGGING # print(resp_text)
    # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    return json.loads(resp_text)

def prepare_headers():
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: prepare_headers')
    hdrs = {
        'Authorization': 'Basic {}'.format(base64.b64encode('{}:{}'.format(client_id, client_secret).encode()).decode()),
	'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    return hdrs

def post_data(data, headers, url):
    # UNCOMMENT FOR DEBUGGING # print('ENTERING: post_data')
    # UNCOMMENT FOR DEBUGGING # print('post_data\nheaders:\n{}\ndata:\n{}\nurl:\n{}'.format(headers, data, url))
    # UNCOMMENT FOR DEBUGGING # print('state right now: {}'.format(state))
    req = urllib.request.Request(url, data=data, headers=headers)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # avoid cert checking
    with urllib.request.urlopen(req, context=gcontext) as response:  # perform POST request and read response
        rsp = response.read()
    return rsp.decode('utf-8')


run(app, host='0.0.0.0', port=app_port)
 
