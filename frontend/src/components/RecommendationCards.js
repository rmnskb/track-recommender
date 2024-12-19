import {useEffect, useState} from "react";
import axios from "axios";

export const RecommendationCards = (tracks) => {
    const [recs, setRecs] = useState([{}])
    const apiUrl = '//localhost:5000'

    useEffect(() => {
            const fetchRecommendations = async () => {
                if (!tracks || tracks.tracks.length === 0) {
                    return;
                }

                const payload = {
                    'ids': Array.isArray(tracks.tracks) ? tracks.tracks : []
                    , 'n_recs': 7
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

    const ListRecommendations = ({recs}) => {
        if (recs.length === 1) return null;

        return (
            recs.map((rec) => (
                <div
                    key={rec['track_id']}
                    className="
                        flex gap-8 flex-wrap justify-center max-w-2xl mx-4
                        sm:max-w-sm md:max-w-sm lg:max-w-sm xl:max-w-sm sm:mx-auto
                        md:mx-auto lg:mx-auto xl:mx-auto mt-8 shadow-xl rounded-lg
                    "
                >
                    <div
                        className="
                            transform max-w-sm bg-white border border-gray-200 rounded-xl shadow-xl
                            dark:bg-gray-800 dark:border-gray-700 transition duration-300 hover:scale-105
                            overflow-hidden
                        "
                    >
                        <div className="justify-center items-center object-cover rounded-t-lg h-96 w-96 overflow-hidden">
                            <img
                                className="rounded-lg object-cover object-top w-full"
                                src={rec['image_url']}
                                alt={rec['track_artist']}
                            ></img>
                        </div>
                        <div className="p-5 text-center mt-2 object-cover">
                            <a href={rec['uri']}>
                                <h5
                                    className="
                                        mb-2 text-2xl font-bold tracking-tight
                                        text-gray-900 dark:text-white
                                    "
                                >{rec['track_name']}</h5>
                                <p
                                    className="mb-3 font-normal text-gray-700 dark:text-gray-400 line-clamp-2"
                                >{rec['artists']}</p>
                            </a>
                        </div>
                    </div>
                </div>
            ))
        );
    };


    return (
        <div className="flex gap-8 flex-wrap justify-center">
            <ListRecommendations recs={recs}/>
        </div>
    );
}