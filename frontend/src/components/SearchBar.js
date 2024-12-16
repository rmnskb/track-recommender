import {useEffect, useRef, useState} from "react";
import axios from "axios";

export const SearchBar = ({chosenTracks, setChosenTracks}) => {
    const [query, setQuery] = useState('')
    const [autocomplete, setAutocomplete] = useState([{}])
    const [selectedIndex, setSelectedIndex] = useState(-1)
    const inputRef = useRef(null)
    const apiUrl = '//localhost:5000'

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
        <form className="flex items-center max-w-sm mx-auto">
            <label htmlFor="search" className="sr-only">Search</label>
            <div className="relative w-full">
                <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                    <svg
                        fill="#6b7280"
                        className="w-4 h-4 text-gray-500 dark:text-gray-400"
                        aria-hidden="true"
                        version="1.1"
                        id="Capa_1"
                        xmlns="http://www.w3.org/2000/svg"
                        width="800px" height="800px" viewBox="0 0 344.156 344.156"
                    >
                      <g>
                        <path d="M343.766,28.723c0-5.525-4.483-10.006-10.006-10.006H106.574c-5.531,0-10.006,4.48-10.006,10.006v194.18
                          c-10.25-8.871-23.568-14.279-38.156-14.279C26.207,208.623,0,234.824,0,267.029c0,32.209,26.207,58.41,58.412,58.41
                          c32.215,0,58.412-26.201,58.412-58.41c0-2.854-0.246-175.924-0.246-175.924h207.176v131.666
                          c-10.229-8.795-23.487-14.148-38.008-14.148c-32.217,0-58.412,26.201-58.412,58.406c0,32.209,26.195,58.41,58.412,58.41
                          c32.205,0,58.41-26.201,58.41-58.41C344.156,264.068,343.766,28.723,343.766,28.723z M58.412,305.43
                          c-21.174,0-38.4-17.227-38.4-38.4c0-21.17,17.227-38.396,38.4-38.396s38.4,17.228,38.4,38.396
                          C96.812,288.203,79.586,305.43,58.412,305.43z M116.578,71.094V38.728h207.176v32.365L116.578,71.094L116.578,71.094z
                          M285.746,305.43c-21.174,0-38.4-17.227-38.4-38.4c0-21.17,17.228-38.396,38.4-38.396s38.4,17.228,38.4,38.396
                          C324.146,288.203,306.92,305.43,285.746,305.43z"/>
                      </g>
                    </svg>
                </div>
                <input
                    type="text" id="search"
                    className="
                       bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg
                       focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5
                       dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
                       dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                    "
                    onChange={handleQueryChange}
                    onKeyDown={handleKeyDown}
                    value={query}
                    ref={inputRef}
                    placeholder="Search tracks..." required
                />
                {query !== "" && autocomplete.length > 0 && (<ListAutocomplete/>)}
            </div>
        </form>
    );
};