import React from 'react'
import './index.css';
import Table from 'react-bootstrap/Table'

function Student(props) {
    const responses = props.student_responses.map(response => (
        <Response response={response} key={response.id}/>
    ));

    return (
        <div className='student'>
            <div>Student #{props.id}</div>
            <div>Story: {props.story}</div>
            <Table striped bordered hover responsive>
                <thead>
                    <tr>
                        <td>Context</td>
                        <td>Question</td>
                        <td>Response</td>
                        <td>Views</td>
                    </tr>
                </thead>
                <tbody>{responses}</tbody>
            </Table>
        </div>
    );
}


function Response(props) {
    const response = props.response;

    return (
        <tr>
            <td>{response.context}</td>
            <td>{response.question}</td>
            <td>{response.response}</td>
            <td>{response.views}</td>
        </tr>
    );
}


class InstructorPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            students: [],
            loaded: false,
        };
    }

    async componentDidMount() {
        try {
            const res = await fetch('/api/add-response/');
            const students = await res.json();
            this.setState({
                students,
                loaded: true,
            });
        } catch (e) {
            console.log(e);
        }
    }

    render() {
        if (this.state.loaded) {
            const students = this.state.students.map(student => (
                <Student story={student.story} student_responses={student.student_responses} id={student.id} key={student.id}/>
            ));

            return students;
        } else {
            return null;
        }
    }
}

export default InstructorPage;
