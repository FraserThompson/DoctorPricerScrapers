import React from 'react';
import PHOListItem from './PHOListItem';
import Utils from './Utils';
import { List, ListSubHeader} from 'react-toolbox/lib/list';

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
          select={this.props.select.bind(this, pho)}
          state={pho.state}
        />
      );
    }, this);

    return (
      <List selectable ripple>
        <ListSubHeader caption='Scrapers' />
        {phoList}
      </List>
    )

  }
}

export default PHOList;