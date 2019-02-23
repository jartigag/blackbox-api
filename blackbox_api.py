#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# let's detach bots from platforms
#
# usage: python3 blackbox_api.py post whatToPost --mastodon

#WIP: remove tweepy dependency

__author__ = "@jartigag"
__version__ = "0.1"

import argparse
import json
import secrets
from datetime import datetime
import urllib.request, urllib.parse
import logging
import time
import random

def post(content,twitter=False,mastodon=False,telegram=False,reply_options=[],verbose=False):
    """post some content on any platform

    args:
        content (str): what to post
        twitter (bool): if True, post it on Twitter
        mastodon (bool): if True, post it on Mastodon
        telegram (bool): if True, post it (either on a chat or a channel) on Telegram
        reply_options (list): if not empty, include predefined reply options to the post (for Telegram)
        verbose (bool): if True, print post info

    returns:
        the post object as a JSON. if error, post=False
    """
    global secrets

    def signature(request, consumer, token):
        #TODO: https://tools.ietf.org/html/draft-hammer-oauth-10#section-3.4
        pass

    if twitter:
        #try:
        header = {'Authorization': 'OAuth\
                oauth_consumer_key="{}",\
                oauth_nonce="{}",\
                oauth_signature="{}",\
                oauth_signature_method="HMAC-SHA1",\
                oauth_timestamp="{}",\
                oauth_token="{}",\
                oauth_version="1.0"'.format(
            secrets.twitter_consumer_key,
            ''.join([str(random.SystemRandom().randint(0, 9)) for i in range(8)]),
            signature(request, consumer, token), #FIXME: "HTTP Error 401: Authorization Required" (oauth_signature isn't ready yet)
            time.time(),
            secrets.twitter_access_token)}
        data = urllib.parse.urlencode({'status': content}).encode('utf8')
        req = urllib.request.Request('https://api.twitter.com/1.1/statuses/update.json?status={}'.format(
            content), headers=header)
        resp = urllib.request.urlopen(req)
        post = json.loads(resp.read().decode('utf8'))

        #post = twitter_api.update_status(content)
        #tweet_url = '{}/{}/status/{}'.format(post.source_url,post.user.screen_name,post.id)
        #if verbose: log.info('%s - \033[1mtweeted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
        #    (post.created_at.strftime('%Y-%m-%d %H:%M:%S'),post.text,tweet_url))
        post = json.loads(post)
        # except Exception as e:
        #     post = False
        #     if verbose: log.error("\n[\033[91m!\033[0m] twitter error: %s" % e)

    if mastodon:
        try:
            header = {'Authorization': 'Bearer {}'.format(secrets.masto_access_token)}
            data = urllib.parse.urlencode({'status': content}).encode('utf8')
            req = urllib.request.Request('https://botsin.space/api/v1/statuses', data, header)
            resp = urllib.request.urlopen(req)
            post = json.loads(resp.read().decode('utf8'))
            if verbose: log.info('%s - \033[1mtooted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
                (post['created_at'],post['content'],post['uri']))
        except Exception as e:
            post = False
            if verbose: log.error("\n[\033[91m!\033[0m] mastodon error: %s" % e)

    if telegram:
        if reply_options:
            reply_markup = '&reply_markup={"keyboard":['+','.join(map('["{0}"]'.format, reply_options))+']}'
        else:
            reply_markup = ''
        try:
            req = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}{}".format(
                secrets.telegram_token, secrets.telegram_chat_id, content, reply_markup)
            resp = urllib.request.urlopen(req)
            post = json.loads(resp.read().decode('utf8'))
            if verbose: log.info('%s - \033[1msent by telegram "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),content,secrets.telegram_chat_id))
        except Exception as e:
            post = False
            if verbose: log.error("\n[\033[91m!\033[0m] telegram error: %s" % e)
    print('debugging:')
    print(post)
    return post

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="let's detach from platforms, v%s by %s" % (__version__,__author__),
        usage="%(prog)s post 'content of the post' [--mastodon --telegram --twitter] [-v]")
    parser.add_argument('action',choices=['post'],
        help='what to do')
    parser.add_argument('content',
        help="action's text/content")
    parser.add_argument('-m','--mastodon',action='store_true',
        help='where: mastodon')
    parser.add_argument('-tg','--telegram',action='store_true',
        help='where: telegram')
    parser.add_argument('-tw','--twitter',action='store_true',
        help='where: twitter')
    parser.add_argument('-r','--reply_options',nargs='+',
            help="list of replies to be chosen")
    parser.add_argument('-v','--verbose',action='store_true',
        help='to print or not to print')
    parser.add_argument('-d','--debug',action='store_true',
                    help='print at debug level')
    args = parser.parse_args()

    log = logging.getLogger(__name__)
    if args.debug:
        logLevel = logging.DEBUG
    elif args.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel, format="[ %(asctime)s %(levelname)s ] " + "%(message)s")

    if args.action=='post':
        post(args.content,args.twitter,args.mastodon,args.telegram,args.reply_options,args.verbose)
