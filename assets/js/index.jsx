import React from 'react';
import ReactDOM from 'react-dom';
import PHOList from './PHOList';
import AdminForm from './AdminForm';

ReactDOM.render(
    <div>
        <PHOList/>
        <AdminForm/>
    </div>,
    document.getElementById('react-app')
);