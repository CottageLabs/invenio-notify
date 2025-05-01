
import React, { Component } from 'react';
import { Dropdown } from "semantic-ui-react";
import { MemberAction } from "./components/MemberAction";

export class ReviewerSearchActions extends Component {
    render() {
        const { result } = this.props;
        return (
            <>
                <Dropdown
                    text='Actions'
                >
                    <Dropdown.Menu>
                        <MemberAction
                            result={result}
                        />
                    </Dropdown.Menu>
                </Dropdown>

            </>
        )
    }
}