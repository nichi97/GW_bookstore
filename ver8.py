from googleapiclient.discovery import build

with open("key.txt", "r") as f:
    api_key = f.readline().strip()
service = build("books", "v1", developerKey=api_key)
vol = service.volumes()
# print(vol)
output = vol.list(q="isbn:9781583671535").execute()
print(output)
