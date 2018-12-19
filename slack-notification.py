#!/usr/bin/env python3

import argparse
import json
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
import sys


"""
Builds and sends a message to Slack for Icinga2 notifications.

TODO: allow passing of name|display_name for services.
"""

def send_message(url, message):
	"""
	POST the message to the Slack webhook URL
	"""
	data = urlencode({"payload": json.dumps(message)}).encode("utf-8")
	response = urlopen(url, data).read()

	if response == b"ok":
		return True
	else:
		print("Error: {}".format(response))
		return False


def parse_options():
	parser = argparse.ArgumentParser(description="Send an Icinga Alert to Slack.com via a generic webhook integration")

	# object
	parser.add_argument('-m', '--message', type=str, metavar="MESSAGE", help="Text of the message")
	parser.add_argument('-s', '--state',   type=str, default="UNKNOWN", choices=["UP", "DOWN", "OK", "WARNING", "CRITICAL", "UNKNOWN"], metavar="STATE", help="An optional object state {default: UNKNOWN}")

	# # notification
	parser.add_argument('-a', '--author',  type=str, metavar="AUTHOR", help="User sending the notification")
	parser.add_argument('-c', '--comment', type=str, metavar="COMMENT", help="Notification comment")
	parser.add_argument('-t', '--type',    type=str, default="CUSTOM", choices=["DOWNTIMESTART", "DOWNTIMEEND", "DOWNTIMEREMOVED", "CUSTOM", "ACKNOWLEDGEMENT", "PROBLEM", "RECOVERY", "FLAPPINGSTART", "FLAPPINGEND"], metavar="TYPE", help="Notification type")

	parser.add_argument('-H', '--host',    type=str, required=True, metavar="HOST", help="Name of the host")
	parser.add_argument('-S', '--service', type=str,                metavar="SERVICE", help="Name of the service")

	parser.add_argument('-w', '--web', type=str, metavar="URL", help="URL of the Icingaweb2 website")

	# Slack
	slack = parser.add_argument_group('Slack')
	slack.add_argument('-u', '--url',     type=str, metavar="URL", help="The Slack webhook URL to send the message to")
	slack.add_argument('-C', '--channel', type=str, metavar="CHANNEL", help="The channel to send the message to")
	slack.add_argument('-T', '--team',    type=str, metavar="TEAM", help="Slack.com team domain")
	slack.add_argument('-O', '--token',   type=str, metavar="TOKEN", help="The access token for your integration")

	args = parser.parse_args()
	return args



def main():
	args = parse_options()

	# TODO: test that we have either a webhook URL or the old token stuff

	type_string = {
		'PROBLEM': 'Problem',
		'ACKNOWLEDGEMENT': 'Acknowledgement',
		'RECOVERY': 'Recovery',
		'CUSTOM': 'Custom',
		'FLAPPINGSTART': 'Flapping Start',
		'FLAPPINGEND': 'Flapping End',
		'DOWNTIMESTART': 'Downtime Start',
		'DOWNTIMEEND': 'Downtime End',
		'DOWNTIMEREMOVED': 'Downtime Removed',
	}

	# colour/emoji tuples for states
	states = {
		'UNKNOWN':  ('#6600CC', ':question:'),
		'CRITICAL': ('danger',  ':bangbang:'),
		'DOWN':     ('danger',  ':bangbang:'),
		'WARNING':  ('warning', ':warning:'),
		'OK':       ('good',    ':white_check_mark:'),
		'UP':       ('good',    ':white_check_mark:'),
	}
	# emoji = states[args.state][1]

	# Only use coloured attachments for certain notification types
	if args.type in ['PROBLEM', 'RECOVERY']:
		colour = states[args.state][0]
	else:
		colour = ""

	fields = [{
		'title': 'Host',
		'value': '<{0}/monitoring/host/show?host={1}|{1}>'.format(args.web, args.host) if args.web is not None else args.host,
		'short': True,
	}]
	if args.service:
		fields.append({
			'title': 'Service',
			'value': '<{0}/monitoring/host/show?host={1}&service={2}|{2}>'.format(args.web, args.host, args.service) if args.web is not None else args.service,
			'short': True,
		})
	fields.append({
		'title': 'State',
		'value': args.state,
		'short': True,
	})
	fields.append({
		'title': 'Output',
		'value': args.message,
		'short': False,
	})

	message = {}
	if args.type == 'PROBLEM':
		message['text'] = "*{}*".format(type_string[args.type])
		message['attachments'] = [
			{
				'fallback': '"{}" on "{}" is {}'.format(args.service, args.host, args.state) if args.service else '"{}" is {}'.format(args.host, args.state),
				'color': colour,
				'fields': fields,
			},
			{
				'fallback': '',
				'color': colour,
				'callback_id': '{0}!{1}'.format(args.host, args.service) if args.service is not None else args.host,
				'actions': [
					{
						'name': 'acknowledge',
						'text': 'Acknowledge',
						'type': 'button',
						'value': 'acknowledge',
					}
				]
			}
		]
	elif args.type == 'ACKNOWLEDGEMENT':
		message['text'] = "*{}* by *{}*{}".format(type_string[args.type], args.author, '\n' + args.comment if args.comment else '')
		message['attachments'] = [
			{
				'fallback': '"{}" on "{}" is {}'.format(args.service, args.host, args.state) if args.service else '"{}" is {}'.format(args.host, args.state),
				'color': colour,
				'fields': fields,
			}
		]
	else:
		message['text'] = "*{}*".format(type_string[args.type])
		message['attachments'] = [
			{
				'fallback': '"{}" on "{}" is {}'.format(args.service, args.host, args.state) if args.service else '"{}" is {}'.format(args.host, args.state),
				'color': colour,
				'fields': fields,
			}
		]

	# Channel can be overridden when using the old incoming-webhooks
	if args.channel:
		message['channel'] = args.channel

	# TODO: use the old token stuff if provided
	if send_message(args.url, message):
		sys.exit(0)
	else:
		sys.exit(1)


if __name__ == "__main__":
	main()
