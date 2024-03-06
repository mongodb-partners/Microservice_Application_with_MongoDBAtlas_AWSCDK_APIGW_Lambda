import React from 'react';
import './App.css';
import TodoList from './TodoList'; // Import the TodoList component

function App() {
    return (
        <div className="App">
            <main>
                <TodoList/> {/* Use the TodoList component here */}
            </main>
        </div>
    );
}

export default App;
