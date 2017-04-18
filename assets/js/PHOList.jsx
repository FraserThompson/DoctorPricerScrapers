import React from 'react';
import PHOListItem from './PHOListItem';
import Utils from './Utils';


class PHOList extends React.Component {
  
  constructor(props) {
    super(props);
  }

  render(){

    var phoList = this.props.list.map(function (pho, index) {
      return (
        <PHOListItem
          key={index}
          name={pho.name}
          last_run={pho.last_run}
          number_of_practices={pho.number_of_practices}
          module={pho.module}
					remove={this.props.remove.bind(this, pho)}
          start={this.props.start.bind(this, pho)}
          select={this.props.select.bind(this, pho)}
          state={pho.state}
        />
      );
    }, this);

    return (
      <ul className="pho-list">
        {phoList}
      </ul>
    )

  }
}

export default PHOList;