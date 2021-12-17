import applemusicpy

secret_key = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgaCrtYljotBnnaeNT
Rpp+/o5wanxSNwLNagqmXE0n7FigCgYIKoZIzj0DAQehRANCAAQCSxx+6eBNDn1c
WbBEcPbMOXrmp+ji2Ygk6sA2Yy77hVBTO+5o7CxL7bYOwVG0Iu70J32xI6r9OaqP
o+lN22po
-----END PRIVATE KEY-----"""
key_id = '745LW89SSA'
team_id = 'Z6J284Z375'


am = applemusicpy.AppleMusic(secret_key=secret_key, key_id=key_id, team_id=team_id)

def search_music(title):
	results = am.search(title, types=['songs'], limit=25)
	result_list = []
	for item in results['results']['songs']['data']:
		attributes = item['attributes']
		artwork = attributes["artwork"]["url"].replace("{w}", "300").replace("{h}", "300")
		data = dict(title = attributes["name"],
			artist= attributes["artistName"],
			preview = attributes["previews"][0]["url"],
			album_art = artwork)
		result_list.append(data)
	return result_list[1:]



# 	{
#     "previews": [
#         {
#             "url": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview116/v4/d7/11/95/d71195c0-291e-ec96-cb50-ad92f998b0b8/mzaf_15801233003829582823.plus.aac.p.m4a"
#         }
#     ],
#     "artwork": {
#         "width": 3000,
#         "height": 3000,
#         "url": "https://is4-ssl.mzstatic.com/image/thumb/Music116/v4/5b/3c/28/5b3c286f-9416-1b46-94f2-0b20e201dc78/886449679881.jpg/{w}x{h}bb.jpg",
#         "bgColor": "081841",
#         "textColor1": "f3fdf5",
#         "textColor2": "809cd8",
#         "textColor3": "c4cfd1",
#         "textColor4": "6882ba"
#     },
#     "artistName": "Mayorkun & Victony",
#     "url": "https://music.apple.com/us/album/holy-father/1591883469?i=1591883478",
#     "discNumber": 1,
#     "genreNames": [
#         "Afrobeats",
#         "Music",
#         "African"
#     ],
#     "durationInMillis": 184000,
#     "releaseDate": "2021-10-27",
#     "name": "Holy Father",
#     "isrc": "UK43Q2114426",
#     "hasLyrics": true,
#     "albumName": "Holy Father - Single",
#     "playParams": {
#         "id": "1591883478",
#         "kind": "song"
#     },
#     "trackNumber": 1,
#     "composerName": "Adewale Mayowa Emmanuel & Victor Ebuka Anthony"
# }