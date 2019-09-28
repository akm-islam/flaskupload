import React, { Component } from 'react';
import LineTo from 'react-lineto';
export default class Lineto extends Component{
    render() {
    return (
        <div>
            <div className="A" style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"200px"}}>Element A</div>
            <div className="B" style={{backgroundColor:"rgb(224,224,224,.3)",width:"100%",height:"200px"}}>Element B</div>
            <LineTo from="A" to="B" />
        </div>
    );
}
}