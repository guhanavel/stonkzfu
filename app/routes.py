from flask import render_template
from flask import current_app as app
from .dash.function import get_events

events = get_events()

@app.route('/')
def home():
    """Landing page."""
    return render_template()


@app.route('/cal')
def cal():
    print(events)
    return render_template("base.html", events=events)
