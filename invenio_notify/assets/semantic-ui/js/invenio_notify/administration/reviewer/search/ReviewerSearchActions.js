
import React, { Component } from 'react';
import { Button, Icon, Dropdown } from "semantic-ui-react";
import { TmpActionA } from "./components/TmpActionA";

export class ReviewerSearchActions extends Component {
    render() {
        return (
            <>
                <h1> ReviewerSearchActions working</h1>
                <Dropdown
                    text='Actions'
                >
                    <Dropdown.Menu>
                        <TmpActionA />
                    </Dropdown.Menu>
                </Dropdown>

            </>
        )
    }
}