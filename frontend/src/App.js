import logo from './logo.svg';
import './App.css';
import {useState} from 'react';
import axios from 'axios'

export default function App() {
    const apiUrl = 'http://localhost:5000'
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
        </div>
    )
}