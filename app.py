from flask import Flask
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

import settings
import database
from database import init_db
from database import Base, Event, Guest, Inviter, GuestEvent, GuestInvites


app = Flask(__name__)


@app.route('/')
def index():
    events = database.session.query(Event).order_by(Event.event.desc()).all()
    stats = {}
    for event in events:
        stats[event.event] = {
            'attending': database.session.query(GuestEvent).filter_by(event=event).filter_by(status='attending').count(),
            'unsure': database.session.query(GuestEvent).filter_by(event=event).filter_by(status='unsure').count(),
            'declined': database.session.query(GuestEvent).filter_by(event=event).filter_by(status='declined').count(),
            'not_replied': database.session.query(GuestEvent).filter_by(event=event).filter_by(status='not_replied').count(),
            'invites': database.session.query(GuestInvites).join(GuestEvent).filter_by(event=event).count()
        }
    return render_template('events.html', events=events, stats=stats)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
