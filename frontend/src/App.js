import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';
import axios from 'axios'

const apiUrl = '//localhost:5000'


const SearchBar = () => {
    const [query, setQuery] = useState('')
    const [autocomplete, setAutocomplete] = useState([{}])
    const [chosenTracks, setChosenTracks] = useState([])

    const inputHandler = (e) => {
        setQuery(e.target.value);
    };

    const fetchAutocomplete = async (query) => {
        try {
            const response = await axios.get(`${apiUrl}/api/v1/autocomplete?q=${query}`);
            console.log('Response structure: ', response.data);
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
                    setChosenTracks(track['track_id']);
                    console.log(track['track_id']);
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

export default function App() {
    const [test, setTest] = useState('')

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
                <SearchBar />
            </div>
        </div>
    );
}