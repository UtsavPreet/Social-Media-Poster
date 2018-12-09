from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slackclient import SlackClient
from pprint import pprint
import redis
from facepy import GraphAPI

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,'SLACK_BOT_USER_TOKEN', None)                                     #
Client = SlackClient(SLACK_BOT_USER_TOKEN)
r = redis.Redis(host=settings.REDIS_HOST)

class Events(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        pprint(slack_message)
        # verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)
            # greet bot
        if 'event' in slack_message:
            event_message = slack_message.get('event')
            pprint(slack_message)

            # ignore bot's own message
            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)

            # process user's message
            user = event_message.get('user')
            text = event_message.get('text')
            channel = event_message.get('channel')
            bot_text = 'Hi <@{}> :wave: how can I help you ?'.format(user)
            if event_message.get('type') == 'app_mention':
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text=bot_text)
                return Response(status=status.HTTP_200_OK)

            if 'setup' in text.lower():
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text='Okay Lets Setup <@{user}>\n Please Enter the Facebook Access Token in the following *format*\n'
                                     '*FB_TOKEN=YOUR_TOKEN*'.format(user=user))
                return Response(status=status.HTTP_200_OK)

            if 'FB_TOKEN' in text:
                r.set('FB_TOKEN',text.split('=')[1])
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text='Setup Done !! <@{user}> Lets start posting'.format(user=user))
                return Response(status=status.HTTP_200_OK)

            if 'post to facebook' in text.lower():
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text='Please provide the text that needs to be posted\n'
                                     'In this format\n'
                                     'FB_POST=*Content To Be Posted*')
                return Response(status=status.HTTP_200_OK)

            if 'FB_POST' in text:
                print(text)
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text='<@{user}> Posted'.format(user=user))
                return Response(status=status.HTTP_200_OK)

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)