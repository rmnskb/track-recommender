# Track Recommender
A simple recommendation engine that recommends tracks based on the user input. The user is able to communicate with it
via simple API endpoint.   
Currently, the project can recommend tracks based on user input, which should be the track IDs, it is planned to
implement broader search functionality to allow to search by album or artist.  
The recommendation engine runs on KDTree algorithm, which establishes the nearest neighbours using tree decisions and then
stores them, so it can be computationally efficient, since it does not have to calculate the distances on each API call.

## How to Install and Use
In order to interact with the project, you need to install Docker, then it is enough to just clone this repository
```shell
git clone https://github.com/rmnskb/track-recommender.git
cd track-recommender
```
Create a ```.env``` file with your desired database credentials:
```shell
echo "POSTGRES_USER=YOUR_POSTGRES_USER" >> .env
echo "POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD" >> .env
echo "POSTGRES_DB=YOUR_POSTGRES_DB" >> .env
```
And run the docker compose: 
```shell
# verify that the docker is installed correctly
docker run hello-world 

# build and run the project
docker-compose up -d --build
```
Please ensure that the default ports ``5432`` and ``5000`` are not used by any other application, please adjust the 
``docker-compose.yaml`` and ``Dockerfile`` file accordingly otherwise.  
At this point, the API should be up and running. At this time, it supports only the POST call that accepts track IDs, an example
call may look like following:
```shell
curl -X POST http://127.0.0.1:5000/api/v1/recommend \
 -H "Content-Type: application/json" \
 -d '{"ids": ["5SuOikwiRyPMVoIQDJUgSV", "1iJBSr7s7jYXzM8EGcbK5b"], "n_recs": 7}'
 
 # or alternatively, a GET request for the autocomplete endpoint
 curl -X GET http://127.0.0.1:5000/api/v1/autocomplete?q=Come
```

As you can see, the first call has two arguments, the track IDs and number of recommendations per song to return.

You can also access the web app using port `:3000` with you browser. The app supports track search within the internal 
database and displays the recommendations for the chosen track.
