import React from 'react';
import ReactDOM from 'react-dom';
import PHOList from './PHOList';

var phoList = [
    {"title": "Southern PHO", "module": "southernpho"}
]

ReactDOM.render(
  <PHOList list={phoList}/>,
   document.getElementById('react-app')
);