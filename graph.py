import requests
import argparse
import dateutil.parser

import settings
import database
from database import init_db
from database import Base, Event, Guest, Inviter, GuestEvent


def execute_request(request):
    r = requests.get('https://graph.facebook.com/%s/%s?access_token=%s' % (event_id, request, settings.ACCESS_TOKEN))
    return r.json


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('event', type=str, help='corresponding event id')
    args = parser.parse_args()

    init_db()

    event_id = args.event
    instance = database.session.query(Event).filter_by(event_id=event_id).first()
    if instance:
        event_db = instance
    else:
        event = execute_request('')
        if event:
            name = event['name']
            owner_fb_id = event['owner']['id']
            owner_fb_name = event['owner']['name']
            description = event['description'] if event.has_key('location') else None
            location = event['location'] if event.has_key('location') else None
            start_time = dateutil.parser.parse(event['start_time']) if event.has_key('start_time') else None
            end_time = dateutil.parser.parse(event['end_time']) if event.has_key('end_time') else None
            event_db = Event(event_id=event_id, name=name, 
                owner_fb_id=owner_fb_id, owner_fb_name=owner_fb_name,
                description=description, location=location, 
                start_time=start_time, end_time=end_time)
            database.session.add(event_db)

    print "[*] Working on '%s' (%s)" % (event_db.name, event_db.event_id)

    invited = execute_request('invited')
    if invited:
        for guest_api in invited['data']:

            instance = database.session.query(Guest).filter_by(fb_id=guest_api['id']).first()
            if instance:
                guest_db = instance
            else:
                guest_db = Guest(fb_id=guest_api['id'], fb_name=guest_api['name'])
                database.session.add(guest_db)
                print "[+] New guest detected: %s" % guest_db.fb_name

            instance = database.session.query(GuestEvent).filter_by(guest=guest_db, event=event_db, status=guest_api['rsvp_status']).first()
            if instance:
                guest_event_db = instance
            else:
                guest_event_db = GuestEvent(guest=guest_db, event=event_db, status=guest_api['rsvp_status'])
                database.session.add(guest_event_db)
                print "[+] New event status for '%s': %s" % (guest_db.fb_name, guest_event_db.status)

    database.session.commit()
