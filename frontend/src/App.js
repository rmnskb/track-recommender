import './App.css';
import {SearchBar} from "./components/SearchBar";
import {RecommendationCards} from "./components/RecommendationCards"
import {useState} from 'react';

export default function App() {
    const [chosenTracks, setChosenTracks] = useState([])

    return (
        <div className="bg-slate-800 flex flex-col min-h-screen justify-center items-center font-SpaceMono">
            <h1 className="
                text-white text-center
                xl:text-5xl lg:text-4xl md:text-3xl
                sm:text-2xl xs:text-xl font-semibold
                bg-gray-800 p-2 bg-opacity-40 rounded-sm mt-11"
            >Music Recommender</h1>
            <br></br>
            <div>
                <SearchBar chosenTracks={chosenTracks} setChosenTracks={setChosenTracks}/>
            </div>
            <br></br>
            <div className="w-[60%]">
                <RecommendationCards tracks={chosenTracks}/>
            </div>
        </div>
    );
}