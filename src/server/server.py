from flask import Flask, render_template, request
import json, csv, re, zlib, base64, requests

app = Flask(__name__)
game = None

LOG_SERVER = 'http://128.237.157.112:5000'

@app.route('/')
def home():
    team = request.args.get('team', '')
    rnd = request.args.get('round', '')
    log = json.dumps('')
    if team != '':
        params = {'team': team, 'round': rnd}
        log = requests.get(LOG_SERVER + '/data', params=params).text
        compressed = re.findall(r'== START GAME OUTPUT --(.*)-- END GAME OUTPUT ==', log)
        if len(compressed) > 0:
            log = zlib.decompress(base64.b64decode(compressed[0]))
        else:
            log = json.dumps({
                'error': ''
            })
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
    try:
        return requests.get(LOG_SERVER + '/teams').text
    except:
        return json.dumps({'error': 'Not available'})

def run_server(g):
    global game
    game = g
    app.run(debug=True)
