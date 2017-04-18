import React from 'react';
import Utils from './Utils';

class PHOListItem extends React.Component {

  constructor(props) {
    super(props);
  }

  render(){
    return (
      <a onClick={this.props.select} href="#"><li>
        <h1>{this.props.name}</h1>
        <h4>{this.props.last_run}</h4>
        <h4>{this.props.number_of_practices}</h4>
        <button type="submit" onClick={this.props.start}>Start</button>
        <button type="submit" onClick={this.props.remove}>Remove</button>
        <h5>{this.props.state}</h5>
      </li></a>
    )
  }
}

export default PHOListItem;