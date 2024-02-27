import React, { useState } from 'react';
import './index.css';

function App() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  const addTodo = (e) => {
    e.preventDefault(); // Prevents the form from refreshing the page
    setTodos([...todos, { id: Date.now(), title: input, completed: false }]);
    setInput(''); // Clear the input after adding
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
      <div className="App container mx-auto mt-10">
        <h1 className="text-4xl mb-4">TODO List</h1>
        <form onSubmit={addTodo} className="mb-4">
          <input
              className="shadow appearance-none border rounded py-2 px-3 text-grey-darker mr-2"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Add a todo"
          />
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
            Add
          </button>
        </form>
        <ul>
          {todos.map(todo => (
              <li key={todo.id} className="flex items-center justify-between mb-2">
                <span className={todo.completed ? 'line-through' : undefined}>{todo.title}</span>
                <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded" onClick={() => deleteTodo(todo.id)}>
                  Delete
                </button>
              </li>
          ))}
        </ul>
      </div>
  );
}

export default App;
