import React from 'react';
import Utils from './Utils';

class PHOListItem extends React.Component {

  constructor(props) {
    super(props);
  }

  render(){
    return (
      <a onClick={this.props.select} href="#"><li>
        <h3>{this.props.name}</h3>
        <h5>Last run: {this.props.last_run}</h5>
        <h5>Number of practices: {this.props.number_of_practices}</h5>
        <pre>{this.props.average_prices}</pre>
        <button type="submit" className="button" onClick={this.props.start}>Start</button>
        <button type="submit" className="button" onClick={this.props.remove}>Remove</button>
        <h5>{this.props.state}</h5>
      </li></a>
    )
  }
}

export default PHOListItem;