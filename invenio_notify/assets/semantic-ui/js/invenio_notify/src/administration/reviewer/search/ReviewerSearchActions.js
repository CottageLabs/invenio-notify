
import React, { Component } from 'react';
import { Dropdown } from "semantic-ui-react";
import { MemberAction } from "./components/MemberAction";

export class ReviewerSearchActions extends Component {
    render() {
        const { result, className } = this.props;
        return (
            <>
                <Dropdown
                    text={"Actions"}
                    icon="cog"
                    floating
                    labeled
                    button
                    className={`icon text-align-center ${className}`}
                >
                    <Dropdown.Menu>
                        <MemberAction
                            reviewer={result}
                        />
                    </Dropdown.Menu>
                </Dropdown>

            </>
        )
    }
}