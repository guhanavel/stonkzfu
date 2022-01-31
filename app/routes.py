import flask
from flask import render_template
from flask import current_app as app
from .dash.function import get_events

events = get_events()


@app.route('/a')
def home():
    return flask.redirect('/')


@app.route('/das')
def dash():
    """Landing page."""
    return flask.redirect('/das')


@app.route('/cal')
def cal():
    print(events)
    return render_template("base.html", events=events)
