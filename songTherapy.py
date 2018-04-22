"""
This is the Song therapy skill. It recommends a song based on the emotion determined by an API
of the user input.
"""

from __future__ import print_function
import urllib2
import urllib
import random


def get_emotion(words):
    url = "https://apis.paralleldots.com/v3/emotion"
    payload = "text=" + words + "&api_key=XXXXXXXX&lang_code=en"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib2.Request(url, payload, headers)
    response = urllib2.urlopen(req)
    emote_response = response.read()
    end = emote_response.find('", "probabilities"')
    emotion = emote_response[38:end]
    return emotion

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText' if '<speak>' not in output else 'SSML',
            'text' if '<speak>' not in output else 'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText' if '<speak>' not in output else 'SSML',
                'text' if '<speak>' not in output else 'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Song Therapy," \
                    " I can give you some help on your current emotional state. " \
                    "Talk to me, I am listening. " \
                    "Maybe, start by describing how your day went so far. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Talk to me, I am listening. Tell me anything, I can help. " \
                    "Maybe, start by describing how your day went so far."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Song Therapy. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_words_to_get_mood_attributes(words_to_get_mood):
    return {"mood": words_to_get_mood}


def gets_mood_in_session(intent, session):
    """ Gets and sets the mood in the session and prepares the speech to reply to the
    user.
    """

    card_title = 'Mood'
    session_attributes = {}
    should_end_session = False

    if 'value' in intent['slots']['WORDS']:
        if session.get('attributes', {}) and "mood" in session.get('attributes', {}):
            #2nd call
            words_to_get_mood = session['attributes']['mood'] + ' ' + intent['slots']['WORDS']['value'][3:]
            mood = get_emotion(words_to_get_mood)
            music = {
                'Happy': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/happy-music/happy2.mp3'],
                'Sad': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/sad-music/Darkness1.mp3',
                'https://s3-us-west-2.amazonaws.com/music-for-song-therapy/sad-music/sad1.mp3',
                'https://s3-us-west-2.amazonaws.com/music-for-song-therapy/sad-music/sad2.mp3'],
                'Sarcasm': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/sarcasm-music/sarcasm1.mp3',
                'https://s3-us-west-2.amazonaws.com/music-for-song-therapy/sarcasm-music/sarcasm2.mp3'],
                'Fear': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/fear-music/fear1.mp3'],
                'Excited': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/excited-music/excited1.mp3',
                'https://s3-us-west-2.amazonaws.com/music-for-song-therapy/excited-music/excited2.mp3'],
                'Angry': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/angry-music/angry1.mp3'],
                'Bored': ['https://s3-us-west-2.amazonaws.com/music-for-song-therapy/bored-music/bored1.mp3',
                'https://s3-us-west-2.amazonaws.com/music-for-song-therapy/bored-music/bored2.mp3']
            }
            output = "<speak> Okay, I've got it. " + "<audio src='"+ random.choice(music[mood]) + "' />  </speak>"
            reprompt_text = "Come again, please. "
            should_end_session = True
        else:
            words_to_get_mood = intent['slots']['WORDS']['value']
            session_attributes = create_words_to_get_mood_attributes(words_to_get_mood)
            mood = get_emotion(words_to_get_mood)
            output = "I sense that you feel " + mood + '. Do you want to tell me more?'
            reprompt_text = "I am sorry but I couldn't quite undersand. Talk to me, I am listening. "\
                        "Maybe, start by describing how your day went so far."
    else:
        output = "Talk to me, I am listening. "\
                    "Maybe, start by describing how your day went so far."
        reprompt_text = "Talk to me, I am listening. "\
                        "Maybe, start by describing how your day went so far."
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "Mood":
        return gets_mood_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
