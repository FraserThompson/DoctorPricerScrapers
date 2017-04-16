import React from 'react';
import PHOListItem from './PHOListItem';
import Utils from './Utils';


class PHOList extends React.Component {
  
  constructor(props) {
    
    super(props);

    var self = this;
    this.state = { 
      phoList: []
    };

    Utils.JsonGet('/scrapers/pho', function(response) {
        self.setState({ phoList: JSON.parse(response.data).results });
    });

  }

  render(){

    var phoList = this.state.phoList.map(function (pho, index) {
      return (
        <PHOListItem
          key={index}
          name={pho.name}
          last_run={pho.last_run}
          module={pho.module}
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