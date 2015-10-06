from flask import Flask, render_template
import json

app = Flask(__name__)
game = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/step')
def step():
    game.step()
    return json.dumps(game.to_dict())

@app.route('/graph')
def graph():
    return json.dumps(game.get_graph())

def run_server(g):
    global game
    game = g
    app.run(debug=True)
