from collections import Counter
from datetime import datetime, timedelta
import getpass, os, email, sys, gmail, dispatch_gmail, re, time, imaplib, string, pywapi
import operator
import unicodedata

from TwitterAPI import TwitterAPI
from chartit import DataPool, Chart
from dispatch.models import UlsterIncident
from dispatch.views import *
from dispatch_gmail.models import IncidentEmail
from dispatch_twitter.models import TwitterIncident
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import json as simplejson
from private import local_settings


def get_twitter_incidents(twitter_username):
    '''
    Creates incidents from a twitter feed -
    given that the status of each status is a sting in dictionary format
    containing the details of a 911 incident.
    
    Using application only authentication from the private module,
    attempt to retrieve as many statuses from one public twitter user as possible,
    using the public Twitter REST API.
    
    Then create a datetime object, save the raw data, normalize it, parse it, and geocode it
    from the unauthenticated Google Maps API V3.
    
    Save each incident to the database.
    '''
    api = TwitterAPI(settings.TWITTER_TOKEN_1, settings.TWITTER_TOKEN_2, settings.TWITTER_TOKEN_3, settings.TWITTER_TOKEN_4)
    r = api.request('statuses/user_timeline', {'screen_name':'%s' % twitter_username, \
                                               #We don't want anything except the statuses.
                                               'exclude_replies':'true', \
                                               # 3,200 is the TwitterAPI rate limit.
                                               'count': '3200', \
                                               #Further reduce our response size by excluding the user's metadata.
                                               'trim_user': 'true', \
                                               #Further reduce our response size by excluding other details
                                               'contributor_details': 'false', \
                                               #The ID of the oldest status to start importing from. 
                                               #This defaults to the oldest possible if the maximum rate limit is reached.
                                               'since_id': '' \
                                               })
    
    for status in r:
        received_datetime = datetime.strptime(status["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        payload = status["text"]
        raw_incident = RawIncident.objects.create(datetime = received_datetime, payload = payload)
        raw_incident.save()
        sys.stdout.write("Saved raw unicode twitter dispatch %s \r" % raw_incident.id)
        sys.stdout.flush()
    return payload, recieved_datetime
