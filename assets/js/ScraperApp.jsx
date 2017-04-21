import React from 'react';
import PHOList from './PHOList';
import Utils from './Utils';
import LogsList from './LogsList';

class ScraperApp extends React.Component {
  
  constructor(props) {
    super(props);
    
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

  handleStart(item) {
    var self = this;

    this.setItemState(item.module, "Running")

    Utils.JsonReq("/dp/scrape", {"module": item.module}, "POST", function(res) {

        if (res.error) {
            self.setItemState(item.module, "Error")
        }  else {
            self.setItemState(item.module, "")
        }

        self.getPhoList();
        self.handleSelect(item);

    })

  }

  render(){
    return (
      <div className="row">
        <div className="large-6 columns">
            <PHOList list={this.state.scrapers} start={this.handleStart.bind(this)} select={this.handleSelect.bind(this)}/>
        </div>
        <div className="large-6 columns">
            <LogsList list={this.state.logs}/>
        </div>
      </div>
    )
  }
}

export default ScraperApp;