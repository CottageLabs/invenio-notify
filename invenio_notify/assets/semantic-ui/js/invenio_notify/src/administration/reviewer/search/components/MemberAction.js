import { ActionModal } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Button, Icon } from "semantic-ui-react";
import { ConnectedMemberForm } from "./MemberForm";

export class MemberAction extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
    };
  }

  onModalTriggerClick = (e) => {
    this.setState({ modalOpen: true });
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
    });
  };

  render() {
    const { reviewer } = this.props;
    const { modalOpen } = this.state;

    return (
      <>
        <Button
          key="manage-members"
          onClick={this.onModalTriggerClick}
          icon
          fluid
          basic
          labelPosition="left"
        >
          <Icon name="users" />
          {i18next.t("Members")}
        </Button>

        <ActionModal modalOpen={modalOpen} result={reviewer}>
          <ConnectedMemberForm
            onClose={this.closeModal}
            reviewerId={reviewer.id}
            actionSuccessCallback={this.props.actionSuccessCallback}
          />
        </ActionModal>
      </>
    );
  }
}

MemberAction.propTypes = {
  reviewer: PropTypes.object.isRequired,
};

