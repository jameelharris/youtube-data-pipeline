import os
import json
import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

CHANNEL_HANDLE = "TritonPoker"
BASE_URL = "https://www.googleapis.com/youtube/v3"
OUTPUT_FILE = "raw_youtube.json"


def get_channel(api_key: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/channels",
        params={
            "key": api_key,
            "part": "snippet,statistics,contentDetails",
            "forHandle": CHANNEL_HANDLE,
        },
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise ValueError(f"No channel found for handle: {CHANNEL_HANDLE}")
    channel = items[0]
    title = channel["snippet"]["title"]
    count = channel["statistics"].get("videoCount", "unknown")
    print(f"Channel: {title}  |  reported video count: {count}")
    return channel


def get_all_video_ids(api_key: str, playlist_id: str) -> list[str]:
    video_ids = []
    params = {
        "key": api_key,
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
    }
    while True:
        resp = requests.get(f"{BASE_URL}/playlistItems", params=params)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        next_token = data.get("nextPageToken")
        if not next_token:
            break
        params["pageToken"] = next_token
    print(f"Video IDs collected: {len(video_ids)}")
    return video_ids


def get_video_details(api_key: str, video_ids: list[str]) -> list[dict]:
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = requests.get(
            f"{BASE_URL}/videos",
            params={
                "key": api_key,
                "part": "snippet,statistics,contentDetails,liveStreamingDetails",
                "id": ",".join(batch),
            },
        )
        resp.raise_for_status()
        videos.extend(resp.json().get("items", []))
    print(f"Video details fetched: {len(videos)}")
    return videos


def main():
    api_key = os.getenv("YT_API_KEY")
    if not api_key:
        raise EnvironmentError("YT_API_KEY not set in environment / .env file")

    channel = get_channel(api_key)
    playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids = get_all_video_ids(api_key, playlist_id)
    videos = get_video_details(api_key, video_ids)

    payload = {
        "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "channel": channel,
        "videos": videos,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    size = os.path.getsize(OUTPUT_FILE)
    print(f"Output written to {OUTPUT_FILE}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
