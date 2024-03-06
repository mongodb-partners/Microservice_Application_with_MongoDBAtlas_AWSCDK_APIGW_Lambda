import React, {useEffect, useState} from 'react';

function TodoList() {
    const [todos, setTodos] = useState([]);

    useEffect(() => {
        const fetchTodos = async () => {
            try {
                const apiEndpoint = "<YOUR_ENDPOINT>"
                const apiToken = "<YOUR_TOKEN>"
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
