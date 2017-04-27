import React from 'react';
import PHOList from './PHOList';
import Utils from './Utils';
import LogsList from './LogsList';

import AppBar from 'react-toolbox/lib/app_bar';

class ScraperApp extends React.Component {

  constructor(props) {
    super(props);

    this.flexCell = {
      "flex": "1",
    }

    this.flexLayout = {
      "display": "flex"
    }

    this.state = { 
      scrapers: [],
      logs: [],
      selected: null
    }
  }

  getPhoList() {
    var self = this;

    Utils.JsonReq('/dp/api/pho', null, "GET", function(response) {
        self.setState({ 'scrapers': JSON.parse(response.data) });
    })
  }

  getLogsList(name) {
    var self = this;

    Utils.JsonReq('/dp/api/logs/?source=' + name, null, "GET", function(response) {
        self.setState({ 'logs': JSON.parse(response.data) });
    })
  }

  componentDidMount() {
    this.getPhoList();
  }

  setItemState(module, state) {
    var self = this

    this.state.scrapers.forEach(function(item, index) {
        if (item.module == module ) self.state.scrapers[index].state = state;
    })

    this.setState({ 'scrapers': this.state.scrapers });
  }

  handleSelect(item) {
      
    var self = this;
    this.setState({ 'selected': item.module });
    this.getLogsList(item.module)

  }

  handleStart() {
    var self = this;

    this.setItemState(this.state.selected, "Running")

    Utils.JsonReq("/dp/scrape", {"module": this.state.selected}, "POST", function(res) {

        if (res.error) {
            self.setItemState(self.state.selected, "Error")
        }  else {
            self.setItemState(self.state.selected, "")
        }

        self.getPhoList();
        self.handleSelect({'module': self.state.selected});

    })

  }

  render(){
    return (
      <div>
        <AppBar title='Doctor Pricer Scrapers'/>
        <div style={this.flexLayout}>
          <div style={this.flexCell}>
            <PHOList list={this.state.scrapers} select={this.handleSelect.bind(this)}/>
          </div>
          <div style={this.flexCell}>
            <LogsList selected={this.state.selected} list={this.state.logs} start={this.handleStart.bind(this)}/>
          </div>
        </div>
      </div>
    )
  }
}

export default ScraperApp;