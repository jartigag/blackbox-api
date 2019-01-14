#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# let's detach bots from platforms
#
# usage: python3 blackbox-api.py post whatToPost --mastodon

__author__ = "@jartigag"
__version__ = "0.1"

import argparse
from mastodon import Mastodon
from telegram import Bot
import secrets
from datetime import datetime

masto_account = Mastodon( access_token=secrets.masto_access_token, api_base_url='https://botsin.space')
tele_bot = Bot(token=secrets.telegram_token)
tele_bot.chat_id = secrets.telegram_chat_id

def post(content,mastodon=False,telegram=False,verbose=False):
	"""post some content on any platform

		args:
			content (str): what to post
			mastodon (bool): if True, post it on Mastodon
			telegram (bool): if True, post it (either on a chat or a channel) on Telegram
			verbose (bool): if True, print post info

		returns:
			the post object
		"""
	post = True
	if mastodon:
		try:
			post = masto_account.toot(content)
			if verbose: print('%s - \033[1mtooted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
				(post.created_at.strftime('%Y-%m-%d %H:%M:%S'),post.content,post.url))
		except Exception as e:
			post = False
			if verbose: print("\n[\033[91m!\033[0m] mastodon error: %s" % e)
	if telegram:
		try:
			tele_bot.send_message(chat_id=tele_bot.chat_id, text=content)
			if verbose: print('%s - \033[1mtooted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
				(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),content,tele_bot.chat_id))
		except Exception as e:
			post = False
			if verbose: print("\n[\033[91m!\033[0m] telegram error: %s" % e)
	return post

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="let's detach from platforms, v%s by @%s" % (__version__,__author__),
		usage="%(prog)s post whatToPost --mastodon")
	parser.add_argument('action',choices=['post'],
		help='what to do')
	parser.add_argument('content',
		help="action's text/content")
	parser.add_argument('-m','--mastodon',action='store_true',
		help='where: mastodon')
	parser.add_argument('-t','--telegram',action='store_true',
		help='where: telegram')
	parser.add_argument('-v','--verbose',action='store_true',
		help='to print or not to print')
	args = parser.parse_args()

	if args.action=='post':
		post(args.content,args.mastodon,args.telegram,args.verbose)
