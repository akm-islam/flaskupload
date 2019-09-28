import React from 'react';
import Lineto from "./components/lineto_test";
import axios from 'axios';
import {Button,Row,Col,Collapse,Navbar,NavbarToggler,NavbarBrand,Nav,NavItem,NavLink,UncontrolledDropdown,DropdownToggle,DropdownMenu,DropdownItem,Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';
export default class Example extends React.Component {
  constructor(props) {
    super(props);
    this.toggle = this.toggle.bind(this);
    this.state = {
      modal: false,
      file:null
    };
  }
  handleFile=(e)=>{
    let file=e.target.files[0]
    this.setState({file:file})
    console.log(e.target.files)
  }
  handleUpload=(e)=>{
    let file=this.state.file;
    let formdata=new FormData()
    formdata.append('image',file)
    formdata.append('name','mamun')
    axios({
      url:'https://c37d7e1c-3801-4b9f-bc9d-2390d4cb1561.mock.pstmn.io/api',
      method:"POST",
      headers:{
        authorizaiotn:'Hello'
      },
      data:formdata
    }).then((res)=>{
      console.log(res)
    },(err)=>{
      console.log(err)
    })
  }
  clickhandler=()=>{
    console.log("Hello world")
  }

  toggle() {
    this.setState(prevState => ({
      modal: !prevState.modal
    }));
  }
  render() {
    return (
      <div>
        <Navbar color="faded" light expand="sm">
          <NavbarBrand href="/">UrbanForest</NavbarBrand>
          <NavbarToggler/>
          <Collapse navbar>
            <Nav className="ml-auto" navbar>
            <UncontrolledDropdown nav inNavbar>
                <DropdownToggle nav caret>
                  Sort by
                </DropdownToggle>
                <DropdownMenu right>
                  <DropdownItem>
                    Atribute
                  </DropdownItem>
                  <DropdownItem>
                    Datasets
                  </DropdownItem>
                </DropdownMenu>
              </UncontrolledDropdown>
              <NavItem>
                <NavLink>Components</NavLink>
              </NavItem>
              <NavItem>
                <Button color="primary" size="md" onClick={this.clickhandler}>Process</Button>
                <Button color="primary" size="md" onClick={this.toggle}>Modal</Button>
              </NavItem>
            </Nav>
          </Collapse>
        </Navbar>
{/* Row starts here */}
        <Row>
          <Col md="2" className="sidebar">
              <div style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"400px"}}>
                <form>
                <input type="file" name="fileupload" id="fileupload" onChange={(e)=>this.handleFile(e)}></input>
                <label htmlFor="fileupload"></label>
                <button type="button" onClick={(e)=>this.handleUpload(e)}>Upload</button>
                </form>
              </div>
          </Col>
          <Col md="10" style={{padding:1}}>
              <div style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"400px"}}>
              </div>
          </Col>
        </Row>
{/* Row starts here */}
        <Modal isOpen={this.state.modal} toggle={this.toggle} backdrop={this.state.backdrop} size="lg">
          <ModalHeader toggle={this.toggle}>Modal title</ModalHeader>
          <ModalBody>
          <Row>
          <Col md="2" style={{padding:1}}>
          <div style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"400px"}}></div>
          </Col>
          <Col md="10" style={{padding:1}}>
          <div style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"400px"}}>
          </div>
          </Col>
        </Row>
          </ModalBody>
        </Modal>

      </div>
    );
  }
}