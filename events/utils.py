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
	results = am.search('travis scott', types=['albums'], limit=5)
	for item in results['results']['albums']['data']:
    	return item['attributes']['name']