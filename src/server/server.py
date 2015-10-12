from flask import Flask, render_template, request
import json, csv, re, zlib, base64, requests

app = Flask(__name__)
game = None

LOG_SERVER = 'http://128.237.157.112:5000'

@app.route('/')
def home():
    team = request.args.get('team', '')
    log = json.dumps('')
    if team != '':
        log = requests.get(LOG_SERVER + '/data', params={'team': team}).text
        print log
        compressed = re.findall(r'== START GAME OUTPUT --(.*)-- END GAME OUTPUT ==', log)[0]
        log = zlib.decompress(base64.b64decode(compressed))
    return render_template('index.html', log=log)

@app.route('/tournament')
def tournament():
    return render_template('tournament.html')

@app.route('/step')
def step():
    game.step()
    return json.dumps(game.to_dict())

@app.route('/graph')
def graph():
    return json.dumps(game.get_graph())

@app.route('/teams')
def teams():
    return urllib2.urlopen(LOG_SERVER + '/teams').read()

def run_server(g):
    global game
    game = g
    app.run(debug=True)
