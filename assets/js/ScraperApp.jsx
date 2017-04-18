import React from 'react';
import PHOList from './PHOList';
import AdminForm from './AdminForm';
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

    Utils.JsonReq('/scrapers/api/pho', null, "GET", function(response) {
        self.setState({ 'scrapers': JSON.parse(response.data) });
    })
  }

  getLogsList(name) {
    var self = this;

    Utils.JsonReq('/scrapers/api/logs/?scraper=' + name, null, "GET", function(response) {
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
    this.setState({ 'selected': item.name });
    this.getLogsList(item.name)

  }

  handleAdd(item){
    var self = this;
    item.last_run = "Never";

    var response = Utils.JsonReq("/scrapers/api/pho/", {"name": item.name, "module": item.module}, "POST", function(res) {
        self.state.scrapers.push(item);
        self.setState({scrapers: self.state.scrapers});
    })
  }

  handleRemove(item){
    var module = item.module

    Utils.JsonReq("/scrapers/api/pho/" + module, null, "DELETE", function(res) {
        console.log(res)
    })

    const remainder = this.state.scrapers.filter((item) => {
      if (item.module !== module) return item
    })

    this.setState({ 'scrapers': remainder })
  }

  handleStart(item) {
    var self = this;

    this.setItemState(item.module, "Running")

    Utils.JsonReq("/scrapers/start", {"module": item.module}, "POST", function(res) {

        if (res.error) {
            self.setItemState(item.module, "Error")
        }  else {
            self.setItemState(item.module, "")
        }

        self.getPhoList();

    })

  }

  render(){
    return (
      <div className="row">
        <div className="large-6 columns">
            <PHOList list={this.state.scrapers} remove={this.handleRemove.bind(this)} start={this.handleStart.bind(this)} select={this.handleSelect.bind(this)}/>
        </div>
        <div className="large-6 columns">
            <LogsList list={this.state.logs}/>
        </div>
        <div className="large-12 columns">
            <AdminForm add={this.handleAdd.bind(this)}/>
        </div>
      </div>
    )
  }
}

export default ScraperApp;