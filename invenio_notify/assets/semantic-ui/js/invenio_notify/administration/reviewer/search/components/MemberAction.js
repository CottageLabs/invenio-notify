/*
* for debugging purpose
* TOBEREMOVED
* */


import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Button, Modal, Icon, Checkbox, List } from "semantic-ui-react";
import { ActionModal } from "@js/invenio_administration";
// import { SetQuotaForm } from "./SetQuotaForm";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";

export class MemberAction extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
    };
  }

  onModalTriggerClick = (e, { payloadSchema, dataName, dataActionKey }) => {
    this.setState({ modalOpen: true });
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
    });
  };


  render() {
    const { result, apiUrl, headerText, isRecord } = this.props;
    const { modalOpen} = this.state;

    return (
      <>
        <Button
          key="set-quota"
          onClick={this.onModalTriggerClick}
          icon
          fluid
          basic
          labelPosition="left"
        >
          <Icon name="users" />
          {i18next.t("Members")}
        </Button>

        <ActionModal modalOpen={modalOpen} result={result}>
          <Modal.Header className="flex justify-space-between">
            <div>{headerText}</div>
            <div>
                <h3> Members </h3>
            </div>
          </Modal.Header>
            <Modal.Content>
                {result && result.members && (
                  <div className="member-list">
                    <h4>{i18next.t("Member Emails")}</h4>
                    <List>
                      {result.members.map((member, index) => (
                        <List.Item key={index}>
                          <Icon name="mail" />
                          <List.Content>{member.email}</List.Content>
                        </List.Item>
                      ))}
                    </List>
                    {result.members.length === 0 && (
                      <p>{i18next.t("No members found.")}</p>
                    )}
                  </div>
                )}
            </Modal.Content>
            <MemberForm
              onClose={this.closeModal}
              result={result}
            />
        </ActionModal>
      </>
    );
  }
}


class MemberForm extends Component {
    constructor(props) {
        super(props);
    }

  render() {
    return (
      <Formik
        onSubmit={this.handleSubmit}
        enableReinitialize
//         initialValues={this.initFormValues()}
        validateOnChange={false}
        validateOnBlur={false}
        validationSchema={this.tombstoneSchema}
      >
        {({ values, handleSubmit }) => {
          return (
            <>
              <Modal.Actions>
{/*                 <Button onClick={this.props.closeModal} floated="left"> */}
                <Button onClick={this.props.onClose} floated="left">
                  {i18next.t("Close")}
                </Button>
              </Modal.Actions>
            </>
          );
        }}
      </Formik>
    );
  }
}

MemberForm.propTypes = {
  onClose: PropTypes.func.isRequired,
  result: PropTypes.object,
};

MemberAction.propTypes = {
  result: PropTypes.object.isRequired,
  apiUrl: PropTypes.string.isRequired,
  headerText: PropTypes.string.isRequired,
  isRecord: PropTypes.bool,
};

MemberAction.defaultProps = {
  isRecord: false,
};

