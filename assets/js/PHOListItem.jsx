import React from 'react';
import Utils from './Utils';

class PHOListItem extends React.Component {

  constructor(props) {
    super(props);
  }

  submit (e){
    e.preventDefault()

    var module = e.currentTarget.getAttribute('data-module')
    Utils.JsonPost("/scrapers/start", {"module": module}, function(res) {
      console.log(res)
    })
  }

  render(){
    return (
      <li>
        <h1>{this.props.name}</h1>
        <h4>{this.props.last_run}</h4>
        <button type="submit" onClick={this.submit} data-module={this.props.module}>Start</button>
      </li>
    )
  }
}

export default PHOListItem;