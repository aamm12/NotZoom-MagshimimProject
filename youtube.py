from googleapiclient.discovery import build

api_key = "AIzaSyAqR5g1vVgpwzpUPlvZDyi9ghcpuBMHlBs"
youtube = build('youtube', 'v3', developerKey=api_key)

def get_videos(name):
	req = youtube.search().list(q=name, part='snippet', type='video', maxResults=10, pageToken=None)
	res = req.execute()
	videos = []
	for i in res["items"]:
		videos.append({"url": "https://www.youtube.com/embed/"+i['id']['videoId'], "jpg": i['snippet']['thumbnails']['medium']['url'], "name": i['snippet']['title']})
	return videos