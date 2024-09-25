import sys
import json

import requests

# read the code first, then realize what you need to do.

# it generates a N_m3u8dl-RE command that you can enter in
# your own terminal to download the recordings you need.

# to archive my lectures on echo360.net.au
# - bryan

# step 1: get PLAY_SESSION cookie. get publicLinkId, mediaId, and sessionId from body content
response = requests.get(sys.argv[1])
playSession = response.headers['Set-Cookie'].split()[0]

body = [x.strip() for x in bytes.decode(response.content, 'utf-8').split('\n') if x.strip()]

gold = body[18][38:-3].replace('\\\"', '\"').replace('\/', '/') # quick html fix

gold = json.loads(gold)

publicId = gold.get('publicLinkId')
mediaId = gold.get('mediaId')
sessionId = gold.get('sessionId')

# step 2: get a token
tokenUrl = f'https://echo360.net.au/api/ui/sessions/{sessionId}'
tokenResponse = requests.get(
    tokenUrl,
    cookies={
        'PLAY_SESSION': playSession
    }
)

token = tokenResponse.headers.get('Token')

# step 3: get media urls
mediaUrl = f'https://echo360.net.au/api/ui/echoplayer/public-links/{publicId}/media/{mediaId}/player-properties'
mediaResponse = requests.get(
    mediaUrl,
    headers={
        'Authorization': f'Bearer {token}'
    },
    cookies={
        'PLAY_SESSION': playSession
    }
)

mediaResponse.raise_for_status()

mediaJson = mediaResponse.json()

# step 4: win?
if mediaJson['status'] == 'ok':
    mediaData = mediaJson['data']
    mediaName = mediaData['mediaName']
    print(mediaName)

    sourceQueryStrings = mediaData['sourceQueryStrings']
    queryStrings = sourceQueryStrings['queryStrings']
    queryString = queryStrings[0]['queryString']

    playableAudioVideo = mediaData['playableAudioVideo']
    playableMedias = playableAudioVideo['playableMedias']

    for media in playableMedias:
        sourceIndex = str(media['sourceIndex'])
        trackType = ','.join(media['trackType'])
        uri = media['uri'].split('?')[0] + f'?{queryString}'
        print(f'{sourceIndex=} {trackType=}')
        if (sys.argv[2] == sourceIndex) and (sys.argv[3] == trackType):
            print(f'./m3u8dl \"{uri}\" --append-url-params -mt -M format=mkv:muxer=mkvmerge --save-name \"{mediaName}\" -sa all -sv best')