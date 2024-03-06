import React, {useEffect, useState} from 'react';
import './TodoList.css'; // Import CSS file for styling

function TodoList() {
    const [todos, setTodos] = useState([]);
    const [newTodoText, setNewTodoText] = useState('');

    useEffect(() => {
        fetchTodos();
    }, []);

    const apiEndpoint = "https://wn5g4w1hj2.execute-api.us-east-1.amazonaws.com/dev/todos";

    const fetchTodos = async () => {
        try {
            const response = await fetch(apiEndpoint);
            const data = await response.json();
            setTodos(data);
        } catch (error) {
            console.error('Error fetching todos:', error);
        }
    };

    const handleCreateTodo = async () => {
        try {
            let body = JSON.stringify({text: newTodoText});
            await fetch(apiEndpoint, {
                method: 'POST', headers: {
                    'Content-Type': 'application/json'
                }, body: body
            });
            setNewTodoText('');
            await fetchTodos();
        } catch (error) {
            console.error('Error creating todo:', error);
        }
    };

    const handleDeleteTodo = async (todoId) => {
        try {
            const body = JSON.stringify({"id": todoId});
            await fetch(apiEndpoint, {
                method: 'DELETE', headers: {
                    'Content-Type': 'application/json'
                }, body: body
            });
            await fetchTodos();
        } catch (error) {
            console.error('Error deleting todo:', error);
        }
    };

    return (<div className="container">
        <h1>My ToDo List</h1>
        <div className="todo-list-container">
            {todos.map(todo => (<p key={todo._id.$oid} className="todo-item">
                {todo.text}
                <button onClick={() => handleDeleteTodo(todo._id.$oid)}>Delete</button>
            </p>))}
        </div>
        <div className="input-container">
            <input
                type="text"
                value={newTodoText}
                onChange={(e) => setNewTodoText(e.target.value)}
            />
            <button onClick={handleCreateTodo}>Add</button>
        </div>
    </div>);
}

export default TodoList;
