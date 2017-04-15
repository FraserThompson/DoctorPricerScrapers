import React from 'react';

class PHOListItem extends React.Component {
  constructor(props) {
    super(props);
  }
  render(){
    return (
      <li>
        <h1>{this.props.title}</h1>
      </li>
    )
  }
}

export default PHOListItem;