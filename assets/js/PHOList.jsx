import React from 'react';
import PHOListItem from './PHOListItem';

class PHOList extends React.Component {
  
  constructor(props) {
    super(props);
  }

  render(){

    var phoList = this.props.list.map(function (pho, index) {
      return (
        <PHOListItem
          key={index}
          title={pho.title}
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