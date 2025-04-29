/*
* for debugging purpose
* TOBEREMOVED
* */


import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Button, Modal, Icon, Checkbox } from "semantic-ui-react";
import { ActionModal } from "@js/invenio_administration";
// import { SetQuotaForm } from "./SetQuotaForm";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";

export class TmpActionA extends Component {
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
    const { resource, apiUrl, headerText, isRecord } = this.props;
    const { modalOpen, setQuotaInBytes } = this.state;

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
          <Icon name="disk" />
          {i18next.t("Tmp A")}
        </Button>

        <ActionModal modalOpen={modalOpen} resource={resource}>
          <Modal.Header className="flex justify-space-between">
            <div>{headerText}</div>
            <div>
                <h3> this is modal header</h3>
            </div>
          </Modal.Header>
            <Modal.Content>
                <h3> this is modal content</h3>
{/*               <p> */}
{/*                 <strong>{i18next.t("Note")}:</strong>{" "} */}
{/*                 {i18next.t( */}
{/*                   "This is the default quota that will be applied to any NEW records created by this user – it will NOT update quota of existing records." */}
{/*                 )} */}
{/*               </p> */}
            </Modal.Content>
            <TmpFormA
            onClose={this.closeModal}
             />
{/*           <SetQuotaForm */}
{/*             actionSuccessCallback={this.handleSuccess} */}
{/*             actionCancelCallback={this.closeModal} */}
{/*             resource={resource} */}
{/*             apiUrl={apiUrl} */}
{/*             setQuotaInBytes={setQuotaInBytes} */}
{/*           /> */}
        </ActionModal>
      </>
    );
  }
}


class TmpFormA extends Component {
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


// SetQuotaAction.propTypes = {
//   resource: PropTypes.object.isRequired,
//   successCallback: PropTypes.func.isRequired,
//   apiUrl: PropTypes.string.isRequired,
//   headerText: PropTypes.string.isRequired,
//   isRecord: PropTypes.bool,
// };
//
// SetQuotaAction.defaultProps = {
//   isRecord: false,
// };

