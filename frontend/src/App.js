import './App.css';
import {useState, useEffect, useRef} from 'react';
import axios from 'axios'

const apiUrl = '//localhost:5000'


const SearchBar = ({chosenTracks, setChosenTracks}) => {
    const [query, setQuery] = useState('')
    const [autocomplete, setAutocomplete] = useState([{}])
    const [selectedProductIndex, setSelectedProductIndex] = useState(-1)
    const inputRef = useRef(null)

    const handleQueryChange = (event) => {
        setQuery(event.target.value);
    };

    const handleKeyDown = (event) => {
        if (event.key === 'ArrowUp') {
            setSelectedProductIndex(prevIndex =>
                prevIndex === -1 ? autocomplete.length - 1 : prevIndex - 1
            )
        } else if (event.key === 'ArrowDown') {
            setSelectedProductIndex(prevIndex =>
                prevIndex === autocomplete.length - 1 ? -1 : prevIndex + 1
            )
        } else if (event.key === 'Enter') {
            if (selectedProductIndex !== -1) {
                setChosenTracks([...chosenTracks, autocomplete[selectedProductIndex]])
                alert(`You selected ${setChosenTracks(autocomplete[selectedProductIndex])['track_artist']}`)
            }
        }
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
            }, 300); // 300ms debounce delay

            return () => clearTimeout(timeoutId); // Cleanup timeout on query change
        } else {
            setAutocomplete([]);
        }
    }, [query]);

    const listAutocomplete = autocomplete.length > 0 ? (
        autocomplete.map(track => (
                <div className="bg-white max-h-96 overflow-y-scroll resultProductContainer">
                    <div
                        key={track['track_id']}
                        className="
                            py-2 px-4 flex items-center justify-between gap-8
                            hover:bg-gray-200 cursor-pointer
                        "
                        onClick={() => {
                            setChosenTracks([...chosenTracks, track['track_id']]);
                        }}
                    >
                        <p>{track['track_artist']}</p>
                    </div>
                </div>
            )
        )
    ) : (
        <></>
    );

    return (
        <div className="max-w-lg mx-auto mt-20 flex flex-col">
            <input
                type="text"
                className="
                    px-4 py-5 border-gray-500
                    focus:outline-none focus:ring-2 focus:border-gray-950
                "
                onChange={handleQueryChange}
                onKeyDown={handleKeyDown}
                value={query}
                ref={inputRef}
                placeholder="Search tracks..."
            />
            {listAutocomplete}
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
        <></>
    );

    return (
        <div>
            {listRecommendations}
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
        <div className="bg-slate-800 flex flex-row min-h-screen justify-center items-center">
            <h1>Music Recommender</h1>
            <button onClick={testApi}>Test the API</button>
            <div>
                <a>{test['api_status']}</a>
            </div>
            <br></br>
            <div>
                <SearchBar chosenTracks={chosenTracks} setChosenTracks={setChosenTracks}/>
            </div>
            <br></br>
            <div>
                <Recommendations tracks={chosenTracks} />
            </div>
        </div>
    );
}