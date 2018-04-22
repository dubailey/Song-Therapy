import urllib2
import urllib
def get_emotion(words):
    url = "https://apis.paralleldots.com/v3/emotion"
    payload = "text=" + words + "&api_key=XXXXXXXXX&lang_code=en"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib2.Request(url, payload, headers)
    response = urllib2.urlopen(req)
    emote_response = response.read()
    end = emote_response.find('", "probabilities"')
    emotion = emote_response[38:end]
    return emotion
print get_emotion("I am scared of spiders")
