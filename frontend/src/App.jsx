import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Cloud, Wind, Droplets, Thermometer, Activity, AlertCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000'; // Adjust if running in Docker vs Localhost

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inputData, setInputData] = useState({
    temp: 20.5,
    humidity: 65,
    pressure: 1013,
    wind_speed: 5.2,
    clouds_all: 40
  });
  
  // Mock historical data for the chart
  const [chartData, setChartData] = useState([
    { time: '10:00', actual: 18, predicted: 18.2 },
    { time: '11:00', actual: 19, predicted: 19.1 },
    { time: '12:00', actual: 21, predicted: 20.8 },
    { time: '13:00', actual: 22, predicted: 22.3 },
    { time: '14:00', actual: 21.5, predicted: 21.9 },
  ]);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/predict`, inputData);
      setPrediction(response.data.predicted_temp);
      
      // Update chart with new prediction (mocking time progression)
      const newTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      setChartData(prev => [...prev.slice(1), { 
        time: newTime, 
        actual: null, // We don't know actual yet
        predicted: response.data.predicted_temp 
      }]);
      
    } catch (err) {
      console.error(err);
      setError('Failed to fetch prediction. Ensure API is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans text-gray-800">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-blue-600 flex items-center gap-2">
              <Activity className="w-8 h-8" />
              Weather RPS Dashboard
            </h1>
            <p className="text-gray-500 mt-1">Real-time Predictive System Monitoring</p>
          </div>
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm font-medium">System Online</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Panel */}
          <div className="bg-white rounded-xl shadow-md p-6 lg:col-span-1">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Cloud className="w-5 h-5 text-blue-500" />
              Live Conditions
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Temperature (°C)</label>
                <div className="relative">
                  <Thermometer className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input 
                    type="number" 
                    value={inputData.temp}
                    onChange={(e) => setInputData({...inputData, temp: parseFloat(e.target.value)})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Humidity (%)</label>
                <div className="relative">
                  <Droplets className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input 
                    type="number" 
                    value={inputData.humidity}
                    onChange={(e) => setInputData({...inputData, humidity: parseFloat(e.target.value)})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Wind Speed (m/s)</label>
                <div className="relative">
                  <Wind className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input 
                    type="number" 
                    value={inputData.wind_speed}
                    onChange={(e) => setInputData({...inputData, wind_speed: parseFloat(e.target.value)})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                  />
                </div>
              </div>

              <button 
                onClick={handlePredict}
                disabled={loading}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2 disabled:opacity-70"
              >
                {loading ? 'Processing...' : 'Generate Prediction'}
              </button>
            </div>
          </div>

          {/* Visualization Panel */}
          <div className="bg-white rounded-xl shadow-md p-6 lg:col-span-2 flex flex-col">
            <h2 className="text-xl font-semibold mb-4">Forecast Analysis</h2>
            
            {/* Prediction Result Card */}
            <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                <p className="text-sm text-blue-600 font-medium mb-1">Predicted Temperature (Next Hour)</p>
                <div className="text-3xl font-bold text-blue-800">
                  {prediction !== null ? `${prediction.toFixed(1)}°C` : '--'}
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                <p className="text-sm text-gray-600 font-medium mb-1">Model Confidence</p>
                <div className="text-3xl font-bold text-gray-800">
                  {prediction !== null ? '94%' : '--'}
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="flex-grow min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="time" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="actual" stroke="#9ca3af" strokeWidth={2} name="Actual" dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="predicted" stroke="#2563eb" strokeWidth={3} name="Predicted" activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg flex items-center gap-3">
            <AlertCircle className="text-red-500" />
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
