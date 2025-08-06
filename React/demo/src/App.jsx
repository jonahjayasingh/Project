import React, { useState } from 'react';
import './App.css';

function App() {
  const [array, setArray] = useState([]);
  const [input, setInput] = useState('');
  const [highlighted, setHighlighted] = useState([]);
  const [sorting, setSorting] = useState(false);
  const [speed, setSpeed] = useState(200); // in milliseconds

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSpeedChange = (e) => {
    setSpeed(Number(e.target.value));
  };

  const handleSubmit = () => {
    const values = input
      .split(',')
      .map((v) => parseInt(v.trim(), 10))
      .filter((v) => !isNaN(v));

    if (values.length === 0) {
      alert('Please enter valid numbers separated by commas.');
      return;
    }

    setArray(values);
    setHighlighted([]);
  };

  const bubbleSort = async () => {
    let arr = [...array];
    setSorting(true);

    for (let i = 0; i < arr.length - 1; i++) {
      for (let j = 0; j < arr.length - i - 1; j++) {
        setHighlighted([j, j + 1]);
        await delay(speed);

        if (arr[j] > arr[j + 1]) {
          [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
          setArray([...arr]);
          await delay(speed);
        }
      }
    }

    setHighlighted([]);
    setSorting(false);
  };

  const clearArray = () => {
    setArray([]);
    setInput('');
    setHighlighted([]);
  };

  return (
    <div className="App">
      <header className="header">
        <h1>Bubble Sort Visualizer</h1>
        <div className="input-section">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Enter numbers like 5, 3, 9"
            disabled={sorting}
          />
          <button onClick={handleSubmit} disabled={sorting}>Submit</button>
          <button onClick={clearArray} disabled={sorting}>Clear</button>
          <button onClick={bubbleSort} disabled={sorting || array.length === 0}>
            Start Sort
          </button>
        </div>
        <div className="speed-control">
          <label htmlFor="speedRange">Animation Speed:</label>
          <input
            type="range"
            id="speedRange"
            min="50"
            max="1000"
            step="50"
            value={speed}
            onChange={handleSpeedChange}
            disabled={sorting}
          />
          <span>{speed} ms</span>
        </div>
      </header>

      <main className="bar-area">
        {array.map((value, index) => (
          <div
            key={index}
            className="bar"
            style={{
              height: `${value * 3}px`,
              backgroundColor: highlighted.includes(index) ? '#f39c12' : '#3498db',
            }}
          >
            <span className="bar-label">{value}</span>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
