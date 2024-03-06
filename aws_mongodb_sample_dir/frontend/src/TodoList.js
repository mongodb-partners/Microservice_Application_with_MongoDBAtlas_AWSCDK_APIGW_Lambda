import React, {useEffect, useState} from 'react';

function TodoList() {
    const [todos, setTodos] = useState([]);

    useEffect(() => {
        const fetchTodos = async () => {
            try {
                // Fetch todos from the backend endpoint with authentication
                const apiEndpoint = process.env.REACT_APP_API_ENDPOINT;
                console.log("API endpoint: ", apiEndpoint)
                let apiToken = process.env.REACT_APP_ID_TOKEN;
                console.log("API endpoint: ", apiToken)
                const response = await fetch(apiEndpoint, {
                    headers: {
                        Authorization: `Bearer ${apiToken}`,
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch todos');
                }
                const data = await response.json();
                setTodos(data);
            } catch (error) {
                console.error('Error fetching todos:', error);
            }
        };

        fetchTodos();
    }, []);

    return (<div>
        <h1>Todo List</h1>
        <ul>
            {todos.map(todo => (<li key={todo.id}>{todo.text}</li>))}
        </ul>
    </div>);
}

export default TodoList;
