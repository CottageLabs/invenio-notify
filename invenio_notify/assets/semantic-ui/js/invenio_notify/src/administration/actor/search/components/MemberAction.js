import { ActionModal } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Button, Icon } from "semantic-ui-react";
import { MemberFormContainer } from "./MemberForm";

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
    const { actor } = this.props;
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

        <ActionModal modalOpen={modalOpen} result={actor}>
          <MemberFormContainer
            onClose={this.closeModal}
            actorId={actor.id}
            actionSuccessCallback={this.props.actionSuccessCallback}
          />
        </ActionModal>
      </>
    );
  }
}

MemberAction.propTypes = {
  actor: PropTypes.object.isRequired,
};

