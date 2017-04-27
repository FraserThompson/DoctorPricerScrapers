import React from 'react';
import Utils from './Utils';
import { ListItem } from 'react-toolbox/lib/list';

class PHOListItem extends React.Component {

  constructor(props) {
    super(props);
  }

  render(){
    return (
      <ListItem caption={this.props.name} legend={"Last Run: " + this.props.last_run + " Number of Practices: " + this.props.number_of_practices + " " + this.props.state} onClick={this.props.select}/>
    )
  }
}

export default PHOListItem;