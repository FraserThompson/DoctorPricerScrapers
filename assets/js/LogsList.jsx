import React from 'react';
import Utils from './Utils';
import LogsListItem from './LogsListItem'

import { Panel } from 'react-toolbox';
import { Button } from 'react-toolbox/lib/button';

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
          id={item.id}
          scraped={JSON.stringify(item.scraped, null, 2)}
          warnings={JSON.stringify(item.warnings, null, 2)}
          errors={JSON.stringify(item.errors, null, 2)}
          changes={JSON.stringify(item.changes, null, 2)}
        />
      );
    }, this);
    
    return (
      <div>
        { this.props.list.length > 0 && 
          <div className="header">
            <Button type="submit" onClick={this.props.start} label={"Start scraping " + this.props.selected }/> 
          </div>
        }
        {logsList}
      </div>
    )
  }
}

export default LogsList;