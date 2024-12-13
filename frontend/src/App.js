import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import axios from 'axios'

const apiUrl = '//localhost:5000'


const SearchBar = ({ chosenTracks, setChosenTracks }) => {
    const [query, setQuery] = useState('')
    const [autocomplete, setAutocomplete] = useState([{}])

    const inputHandler = (e) => {
        setQuery(e.target.value);
    };

    const fetchAutocomplete = async (query) => {
        try {
            const response = await axios.get(`${apiUrl}/api/v1/autocomplete?q=${query}`);
            setAutocomplete(response.data);
        } catch (error) {
            console.error('Error fetching the autocomplete: ', error);
            setAutocomplete([]);
        }
    }

    useEffect(() => {
        if (query.length > 2) {
            const timeoutId = setTimeout(() => {
                fetchAutocomplete(query);
            }, 300); // Adjust debounce delay as needed (300ms is typical)

            return () => clearTimeout(timeoutId); // Cleanup timeout on query change
        } else {
            setAutocomplete([]);
        }
    }, [query]);

    const listAutocomplete = autocomplete.length > 0 ? (
        autocomplete.map(track =>
            <li
                key={track['track_id']}
                onClick={() => {
                    setChosenTracks([...chosenTracks, track['track_id']]);
                }}
                className="active"
            >
                {track['track_artist']}
            </li>
        )
    ) : (
        <li>No suggestions available</li>
    );

    return (
        <div>
            <input
            type="text"
            placeholder="Enter your search here"
            onChange={inputHandler}
            value={query}
        />
        <ul>{autocomplete && listAutocomplete}</ul>
        </div>
    );
}


const Recommendations = (tracks) => {
    const [recs, setRecs] = useState([{}])

    useEffect(() => {
            const fetchRecommendations = async () => {
                if (!tracks || tracks.tracks.length === 0) {
                    return;
                }

                const payload = {
                    'ids': Array.isArray(tracks.tracks) ? tracks.tracks : []
                    , 'n_recs': 5
                };

                try {
                    const response = await axios.post(
                        `${apiUrl}/api/v1/recommend`
                        , payload
                    );
                    setRecs(response.data)
                } catch (error) {
                    console.error('Error fetching recommendations:', error);
                }
            };
            fetchRecommendations();
        }, [tracks]
    );

    const listRecommendations = recs.length > 0 ? (
        recs.map(rec =>
            <li
                key={rec['track_id']}
            >
                {rec['track_artist']}
            </li>
        )
    ) : (
        <li>No recommendations</li>
    );

    return (
      <div>
          <li>
              {recs && listRecommendations}
          </li>
      </div>
    );
}

export default function App() {
    const [test, setTest] = useState('')
    const [chosenTracks, setChosenTracks] = useState([])

    const testApi = async () => {
        try {
            const response = await axios.get(`${apiUrl}/api/v1/test`);
            setTest(response.data)
        } catch (error) {
            console.error('Error testing the API: ', error)
        }
    }

    return (
        <div>
            <h1>Music Recommender</h1>
            <button onClick={testApi}>Test the API</button>
            <div>
                <a>{test['api_status']}</a>
            </div>
            <div>
                <SearchBar chosenTracks={chosenTracks} setChosenTracks={setChosenTracks} />
            </div>
            <div>
                <Recommendations tracks={chosenTracks} />
            </div>
        </div>
    );
}