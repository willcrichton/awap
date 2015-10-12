from flask import Flask, render_template, request
import json, csv, urllib2, urllib, re, zlib

app = Flask(__name__)
game = None

LOG_SERVER = 'http://unix6.andrew.cmu.edu:15213/jlareau%40andrew.cmu.edu_6_awapcompetition_autograde.txt'

@app.route('/')
def home():
    team = request.args.get('team', '')
    log = ''
    if team != '':
        data = {}
        data['team'] = team
        url = LOG_SERVER + '?' + urllib.urlencode(data)
        log = urllib2.urlopen(url).read()
        compressed = re.findall(r'== START GAME OUTPUT --\n(.*)\n-- END GAME OUTPUT ==', log, re.DOTALL)[0]
        log = zlib.decompress(compressed, zlib.MAX_WBITS | 16)
        print log
    return render_template('index.html', log=json.dumps(log))

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
    with open('awapteams.csv', 'r') as f:
        lines = f.read().split("\r")
        teams = [line.split(",")[0] for line in lines]
        teams.sort()
        return json.dumps(teams)

def run_server(g):
    global game
    game = g
    app.run(debug=True)
