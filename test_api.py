import os
import requests

API_KEY = os.environ["YT_API_KEY"]

# Resolve the Triton channel from its @handle
resp = requests.get(
    "https://www.googleapis.com/youtube/v3/channels",
    params={
        "part": "snippet,statistics,contentDetails",
        "forHandle": "TritonPoker",
        "key": API_KEY,
    },
)

data = resp.json()

if resp.status_code != 200:
    print("ERROR", resp.status_code)
    print(data)
else:
    ch = data["items"][0]
    print("Channel:", ch["snippet"]["title"])
    print("Channel ID:", ch["id"])
    print("Subscribers:", ch["statistics"].get("subscriberCount"))
    print("Total videos:", ch["statistics"].get("videoCount"))
    print("Total views:", ch["statistics"].get("viewCount"))
    print("Uploads playlist:", ch["contentDetails"]["relatedPlaylists"]["uploads"])