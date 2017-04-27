import React from 'react';
import Utils from './Utils';

import { Card, CardMedia, CardTitle, CardText, CardActions } from 'react-toolbox/lib/card';
import Chip from 'react-toolbox/lib/chip';
import {Tab, Tabs} from 'react-toolbox';

class LogsListItem extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      index: 1
    }
  }

  handleTabChange(index) {
    this.setState({index});
  };

  render(){
    return (
      <Card>
        <CardTitle title={this.props.id + " - " + this.props.date}/>
        <CardText>
          <Tabs index={this.state.index} onChange={this.handleTabChange.bind(this)}>
            <Tab label={"Errors " + this.props.errors.length}>
              <pre>{this.props.errors}</pre>
            </Tab>
            <Tab label={"Warnings " + this.props.warnings.length}>
              <pre>{this.props.warnings}</pre>
            </Tab>
            <Tab label={"Changes " + this.props.changes.length}>
              <pre>{this.props.changes}</pre>
            </Tab>
            <Tab label={"Scraped " + this.props.scraped.length}>
              <pre>{this.props.scraped}</pre>
            </Tab>
          </Tabs>
        </CardText>
      </Card>
    )
  }
}

export default LogsListItem;