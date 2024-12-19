source .env

# Send a sample call to authenticate the app
curl -X POST https://accounts.spotify.com/api/token \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "grant_type=client_credentials&client_id=${SPOTIFY_ID}&client_secret=${SPOTIFY_SECRET}"
