import React from 'react';
import Utils from './Utils';

class LogsListItem extends React.Component {

  constructor(props) {
    super(props);
  }

  render(){
    return (
      <li>
        <h3>{this.props.date}</h3>
        <h4>Scraped</h4>
        <pre>{this.props.scraped}</pre>
        <h4>Warnings</h4>
        <pre>{this.props.warnings}</pre>
        <h4>Errors</h4>
        <pre>{this.props.errors}</pre>
      </li>
    )
  }
}

export default LogsListItem;