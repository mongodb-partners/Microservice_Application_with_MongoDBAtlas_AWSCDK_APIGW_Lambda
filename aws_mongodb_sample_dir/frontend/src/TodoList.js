import React, {useEffect, useState} from 'react';

function TodoList() {
    const [todos, setTodos] = useState([]);
    const [newTodoText, setNewTodoText] = useState('');

    useEffect(() => {
        fetchTodos();
    }, []);

    const apiEndpoint = "https://o72ork5oub.execute-api.us-east-1.amazonaws.com/dev/todos";

    const fetchTodos = async () => {
        try {
            const response = await fetch(apiEndpoint);
            const data = await response.json();
            console.log(data);
            setTodos(data);
        } catch (error) {
            console.error('Error fetching todos:', error);
        }
    };

    const handleCreateTodo = async () => {
        try {
            let body = JSON.stringify({text: newTodoText});
            console.log(body);
            const response = await fetch(apiEndpoint, {
                method: 'POST', headers: {
                    'Content-Type': 'application/json'
                }, body: body
            });
            console.log(response.json());
            setNewTodoText('');
            await fetchTodos();
        } catch (error) {
            console.error('Error creating todo:', error);
        }
    };

    const handleDeleteTodo = async (todoId) => {
        try {
            console.log("todoId", todoId);
            const body = JSON.stringify({"id": todoId});
            console.log("delete body", body);
            const response = await fetch(apiEndpoint, {
                method: 'DELETE', headers: {
                    'Content-Type': 'application/json'
                }, body: body
            });
            console.log(response.json());
            await fetchTodos();
        } catch (error) {
            console.error('Error deleting todo:', error);
        }
    };

    return <div>
        <h1>Todo List</h1>
        <input
            type="text"
            value={newTodoText}
            onChange={(e) => setNewTodoText(e.target.value)}
        />
        <button onClick={handleCreateTodo}>Add Todo</button>
        <ul>
            {todos.map(todo => <li key={todo._id.$oid}>
                {todo.text}
                <button onClick={() => handleDeleteTodo(todo._id.$oid)}>Delete</button>
            </li>)}
        </ul>

    </div>;
}

export default TodoList;
