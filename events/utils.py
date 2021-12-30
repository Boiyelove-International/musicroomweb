import pprint
import random, string
import applemusicpy
from fcm_django.models import FCMDevice
from .serializers import SongSerializer
from .models import Song

secret_key = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgaCrtYljotBnnaeNT
Rpp+/o5wanxSNwLNagqmXE0n7FigCgYIKoZIzj0DAQehRANCAAQCSxx+6eBNDn1c
WbBEcPbMOXrmp+ji2Ygk6sA2Yy77hVBTO+5o7CxL7bYOwVG0Iu70J32xI6r9OaqP
o+lN22po
-----END PRIVATE KEY-----"""
key_id = '745LW89SSA'
team_id = 'Z6J284Z375'


am = applemusicpy.AppleMusic(secret_key=secret_key, key_id=key_id, team_id=team_id)




def clean_song_data(song):
	attributes = song['attributes']
	artwork = attributes["artwork"]["url"].replace("{w}", "300").replace("{h}", "300")
	return dict(song_title = attributes["name"],
						artist_name= attributes["artistName"],
						song_url = attributes["previews"][0]["url"],
						album_art = artwork,
						apple_song_id =  "%s" % song["id"])

def check_song_in_list(song_dict, list_item):
		item = "{}".format(song_dict["id"])
		if  item in list_item:
			return True
		return False

def search_music(title):
	url = "https://api.music.apple.com/v1/catalog/us/search?term=%s&limit=25&types=songs" % title.replace(" ", "+")
	results = am._get(url)
	# results = am.search(title, storefront="ng", types=['songs',], limit=25)
	# pprint.pprint(results)
	result_list = []
	if results['results']:
		songs = results["results"]["songs"]["data"]

		songs_id = [x["id"] for x in songs]
		existing_songs = Song.objects.filter(apple_song_id__in=songs_id)
		if existing_songs.exists():
			songs_id = list(set(existing_songs.values_list("apple_song_id", flat=True)))
			# print("existing songs id are", songs_id)
		# Todo: Re-evaluate the following line to filter exting songs
		result_list = [clean_song_data(song_dict) for song_dict in songs]
		songs = [Song(**clean_song_data(song_dict)) for song_dict in songs]
		
		# print("songs is", songs)
		Song.objects.bulk_create(songs, ignore_conflicts=True)
		# print("songs created are", len(result_list))

		# for item in results['results']['songs']['data']:
			
			# attributes = item['attributes']
			# artwork = attributes["artwork"]["url"].replace("{w}", "300").replace("{h}", "300")
			# data = dict(title = attributes["name"],
			# 	artist= attributes["artistName"],
			# 	preview = attributes["previews"][0]["url"],
			# 	album_art = artwork,
			# 	apple_song_id =  item["id"])
			# result_list.append(clean_song_data(data))
	return result_list


	

def send_notification(user_ids, title, message, data):
	try:
		device = FCMDevice.objects.filter(user__in=user_ids).first()
		result = device.send_message(title=title, data=data, sound=True)
		return result
	except:
		pass


def gen_code(k=4):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(k))


def create_sample_events():
	from django.contrib.auth.models import User
	from accounts.models import PartyGuest
	from  events.models import Event
	# Event.objects.all().delete()
	# PartyGuest.objects.all().delete()
	from accounts.factories import PartyGuestFactory
	u = User.objects.get(email="roland@boiyelove.website")
	from .factories import EventFactory
	pg_list = PartyGuestFactory.create_batch(size=15)
	events = EventFactory.create_batch(size=20, organizer=u, attendees = pg_list)
	return events

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