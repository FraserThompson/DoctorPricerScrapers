import React from 'react';
import Utils from './Utils';
import LogsListItem from './LogsListItem'

class LogsList extends React.Component {

  constructor(props) {
    super(props);
  }

  render(){

    var logsList = this.props.list.map(function (item, index) {
      return (
        <LogsListItem
          key={index}
          date={item.date}
          scraped={item.scraped}
          warnings={item.warnings}
          errors={item.errors}
        />
      );
    }, this);
    
    return (
      <ul className="log-list">
        {logsList}
      </ul>
    )
  }
}

export default LogsList;