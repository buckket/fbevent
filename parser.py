import re
from bs4 import BeautifulSoup

import database
from database import init_db
from database import Base, Event, Guest, Inviter, GuestEvent, GuestInvites


def get_guest(element):
    string = element.find_parents('div', 'clearfix')[1].contents[0].get('data-hovercard')
    match = re.search('(.*)id=(\d*)', string)
    if match:
        fb_id = match.group(2)
        instance = database.session.query(GuestEvent).join(Guest).filter(Guest.fb_id == fb_id).first()
        if instance:
            return instance


def get_inviter(name):
    instance = database.session.query(Inviter).filter_by(name=name).first()
    if instance:
        return instance
    else:
        inviter = Inviter(name=name)
        database.session.add(inviter)
        return inviter


def perform_action(guest, inviter):
    guest_event_db = get_guest(element)
    inviter_db = get_inviter(inviter)
    if guest_event_db and inviter_db:
        instance = database.session.query(GuestInvites).filter_by(invited=guest_event_db).filter_by(inviter=inviter_db).first()
        if not instance:
            print "[+] %s invited %s" % (inviter_db.name, guest_event_db.guest.fb_name)
            guest_invite_db = GuestInvites(invited=guest_event_db, inviter=inviter_db)
            database.session.add(guest_invite_db)


if __name__ == "__main__":

    init_db()

    with open("test.txt") as f:
        data = f.read()
        soup = BeautifulSoup(data)

        for element in soup.select('.fbEventGuestInviters'):
            label = element.get('aria-label')

            # own invites
            # wip

            # single invites
            match = re.search('(.*) hat (.*) eingeladen.', label)
            if match:
                inviter = match.group(1)
                perform_action(guest=element, inviter=inviter)

            # multi invites
            match = re.search('(.*) wurde eingeladen von:',label)
            if match:
                lines = label.splitlines()
                for line in lines[1:]:
                    perform_action(guest=element, inviter=line)

        database.session.commit()
