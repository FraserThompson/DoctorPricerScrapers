import React from 'react';
import Utils from './Utils';

class AdminForm extends React.Component {
  
  constructor(props) {
    super(props);
  }

  submit (e){
    e.preventDefault()

    var formData = new FormData(e.target)

    var module = e.currentTarget.getAttribute('data-module')
    var response = Utils.JsonPost("/scrapers/pho/", {"name": formData.get('name'), "module": formData.get('module')}, function(res) {
        console.log(res);
    })
  }

  render(){
    return (
        <form onSubmit={this.submit} id="adminForm">
            <input type="text" name="name"/>
            <input type="text" name="module"/>
            <button type="submit">Add</button>
        </form>
    )
  }
}

export default AdminForm;