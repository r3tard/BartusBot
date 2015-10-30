﻿import StringIO
import json
import logging
import random
import urllib
import urllib2
import requests
import facebook_utils
import warnings
import datetime
import time
from bs4 import BeautifulSoup
import utils

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

plan = utils.Plan()
facebook = facebook_utils.Facebook()

warnings.filterwarnings('ignore', category=DeprecationWarning) # dałem to, bo moduł facebook jest troche stary i wyskakują błędy i moze pomoze

#TOKEN TELEGRAMA NIE DOTYKAC PEDAŁY XD
TOKEN = '129060792:AAGFH7v-zyS-PfX1I_-FOSIvm6vAAH9Yi-U'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

#app_secret = '417a9e046897e14bb66eac1c3f1c7451'
#app_id = '985465174848513'


#TOKEN REQUEST HHTPS





"""
url_last_picture = 'https://graph.facebook.com/film.czeski/feed?fields=full_picture&limit=1&access_token=' + access_token
responseIMG = requests.get(url_last_picture)
decoded_json_IMGDATA = responseIMG.json()

postNodeIMG = decoded_json_IMGDATA["data"][0]["full_picture"]

"""





# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return


        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
                """
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
                """
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start bartusbot':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop bartusbot':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/news@BartusBot' or text == '/news':
                reply(facebook.postNode['message'])
                #reply(img=urllib2.urlopen(postNodePIC).read())

            elif text == '/test':
                reply('Działam')
            elif text == '/poniedzialek':
                reply(plan.lekcje_dzien(0))
            elif text == '/wtorek':
                reply(plan.lekcje_dzien(1))
            elif text == '/sroda':
                reply(plan.lekcje_dzien(2))
            elif text == '/czwartek':
                reply(plan.lekcje_dzien(3))
            elif text == '/piatek':
                reply(plan.lekcje_dzien(4))
            elif text == '/jutro':
                reply(plan.lekcje_dzien(datetime.datetime.now().weekday()+1))
            elif text == '/nastepna':
                reply(plan.nastepna_lekcja(datetime.datetime.now()))

        elif 'wojna' in text:
            reply('wojna gej')
            
           


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
