import './App.css';
import {useState, useEffect, useRef} from 'react';
import axios from 'axios'

const apiUrl = '//localhost:5000'


const SearchBar = ({chosenTracks, setChosenTracks}) => {
    const [query, setQuery] = useState('')
    const [autocomplete, setAutocomplete] = useState([{}])
    const [selectedIndex, setSelectedIndex] = useState(-1)
    const inputRef = useRef(null)

    const resetSearch = () => {
        setQuery("");
        setAutocomplete([]);
        setSelectedIndex(-1);
    };

    const handleQueryChange = (event) => {
        setQuery(event.target.value);
    };

    const handleKeyDown = (event) => {
        switch (event.key) {
            case 'ArrowUp':
                event.preventDefault();
                setSelectedIndex(prevIndex =>
                    prevIndex === -1 ? autocomplete.length - 1 : prevIndex - 1
                );
                break;
            case 'ArrowDown':
                event.preventDefault();
                setSelectedIndex(prevIndex =>
                    prevIndex === autocomplete.length - 1 ? -1 : prevIndex + 1
                )
                break;
            case 'Enter':
                if (selectedIndex !== -1) {
                    setChosenTracks([...chosenTracks, autocomplete[selectedIndex]['track_id']])
                    resetSearch();
                }
                break;
            case 'Escape':
                resetSearch();
                break;
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

    const ListAutocomplete = () => {
        const scrollActiveItemIntoView = (index) => {
            const activeItem = document.getElementById(`item-${index}`)

            if (activeItem) {
                activeItem.scrollIntoView({
                    block: "nearest",
                    inline: "start",
                    behavior: "smooth"
                });
            }
        };

        useEffect(() => {
            if (selectedIndex !== -1) {
                scrollActiveItemIntoView(selectedIndex)
            }
        }, [selectedIndex]);

        return (
            <div className="bg-white max-h-96 overflow-y-scroll resultProductContainer">
                {autocomplete.map((track, index) => (
                    <div
                        key={track['track_id']}
                        id={`item-${index}`}
                        className={`
                            ${selectedIndex === index ? "bg-gray-500" : ""}
                            py-2 px-4 flex items-center justify-between gap-8
                            hover:bg-gray-200 cursor-pointer
                        `}
                        onClick={() => {
                            setChosenTracks([...chosenTracks, track['track_id']]);
                            resetSearch();
                        }}
                    >
                        <p>{track['track_artist']}</p>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="flex flex-col max-w-lg mx-auto mt-20">
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
            {query !== "" && autocomplete.length > 0 && (<ListAutocomplete/>)}
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
                <Recommendations tracks={chosenTracks}/>
            </div>
        </div>
    );
}