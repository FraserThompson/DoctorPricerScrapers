import React from 'react';

class AdminForm extends React.Component {
  
  constructor(props) {
    super(props);

    this.state = { 
      'name': "",
      'module': ""
    };
  }

  handleChange(e) {
    e.preventDefault();

    this.setState({ [e.target.name]: e.target.value })
  }

  render(){

    return (
      <div>
        <input type="text" name="name" value={this.state.name} onChange={this.handleChange.bind(this)}/>
        <input type="text" name="module" value={this.state.module} onChange={this.handleChange.bind(this)}/>
        <button onClick={this.props.add.bind(this, this.state)}>Add</button>
      </div>
    )
  }
}

export default AdminForm;