import './App.css';
import {SearchBar} from "./components/SearchBar";
import {useState, useEffect, useRef} from 'react';
import axios from 'axios'

const apiUrl = '//localhost:5000'


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