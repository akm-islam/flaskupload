/*
uploadtest/templates/upload.html is for testing the program with flask
handleFile function responds to change in input field.
handleUpload function does the upload operation
To upload multiple files we iterate objects and add them to multi part object with the tag 'file'
*/
import React from 'react';
import axios from 'axios';
export default class Example extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      modal: false,
      file:{}
    };
  }
  handleFile=(e)=>{
    let file=e.target.files
    this.setState({file:file})
  }
  handleUpload=(e)=>{
    let file=this.state.file;
    let formdata=new FormData()
    for (var key in this.state.file) {
    formdata.append('file',this.state.file[key])
    }
    axios({
      url:'http://localhost:5000/uploader',
      method:"POST",
      headers:{
      authorizition:'Hello'
      },
      data:formdata
    }).then((respose_from_server)=>{
    // then is the response
      console.log(respose_from_server.data)
    },(err)=>{
      console.log(err)
    })
  }
  render() {
    return (
      <div>
{/* Row starts here */}
              <div style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"400px"}}>
              <form action = "http://localhost:5000/uploader" method = "POST" >
                <input type="file" name="fileupload" id="fileupload" onChange={(e)=>this.handleFile(e)} multiple={true}></input>
                <label htmlFor="fileupload"></label>
                <button type="button" onClick={(e)=>this.handleUpload(e)}>Upload</button>
                </form>
              </div>
{/* Row starts here */}
      </div>
    );
  }
}