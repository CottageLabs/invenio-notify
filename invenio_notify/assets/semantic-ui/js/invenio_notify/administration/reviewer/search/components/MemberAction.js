import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Button, Modal, Icon, Checkbox, List } from "semantic-ui-react";
import { ActionModal } from "@js/invenio_administration";
// import { SetQuotaForm } from "./SetQuotaForm";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";
import { TextAreaField, ErrorMessage } from "react-invenio-forms";
import * as Yup from "yup";
import { withCancel, http } from "react-invenio-forms";
import { NotificationContext } from "@js/invenio_administration";

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
    const { modalOpen, } = this.state;

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
          <MemberForm
            onClose={this.closeModal}
            reviewer={reviewer}
          />
        </ActionModal>
      </>
    );
  }
}

class MemberForm extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
      error: undefined,
      reviewer: props.reviewer || null,
    };

    this.emailSchema = Yup.object({
      emails: Yup.string().required(i18next.t("Email is required")),
    });
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  componentDidUpdate(prevProps) {
    // Update state if reviewer prop changes
    if (prevProps.reviewer !== this.props.reviewer) {
      this.setState({ reviewer: this.props.reviewer });
    }
  }

  updateReviewer = (updatedReviewer) => {
    this.setState({ reviewer: updatedReviewer });
  };

  static contextType = NotificationContext;

  handleSubmit = async (values, { resetForm }) => {
    this.setState({ loading: true });

    const { addNotification } = this.context;
    const { actionSuccessCallback } = this.props;
    const { reviewer } = this.state;

    const apiUrl = `/api/reviewer/${reviewer.id}/member`;

    console.log("Submit member with email:", values.emails);

    const emails = values.emails
      .split(/[\s,]+/)
      .map(email => email.trim())
      .filter(email => email);

    console.log("Parsed email list:", emails);

    this.cancellableAction = withCancel(
      http.post(apiUrl, {
        emails,
      })
    );

    try {
      const response = await this.cancellableAction.promise;
      this.setState({ loading: false, error: undefined });

      resetForm();

      addNotification({
        title: i18next.t("Success"),
        content: i18next.t("Added memeber {{member}}", {
          member: emails.join(", "),
        }),
        type: "success",
      });

      this.updateReviewer(response.data);

      if (actionSuccessCallback) {
        actionSuccessCallback();
      }
    } catch (error) {
      if (error === "UNMOUNTED") return;

      this.setState({
        error: error?.response?.data?.message || error?.message,
        loading: false,
      });
      console.error(error);
    }
  };

  initFormValues = () => {
    return {
      emails: "",
    };
  };

  render() {
    const { error, loading } = this.state;
    const { } = this.props;
    const { reviewer } = this.state;

    return (
      <Formik
        onSubmit={this.handleSubmit}
        enableReinitialize
        initialValues={this.initFormValues()}
        validateOnChange={false}
        validateOnBlur={false}
        validationSchema={this.emailSchema}
      >
        {({ handleSubmit }) => {
          return (
            <>
              {error && (
                <Modal.Content>
                  <ErrorMessage
                    header={i18next.t("Unable to add member.")}
                    content={i18next.t(error)}
                    icon="exclamation"
                    className="text-align-left"
                    negative
                  />
                </Modal.Content>
              )}
              <Modal.Header className="flex justify-space-between">
                <div>
                  <h3> {i18next.t("Members")} </h3>
                </div>
              </Modal.Header>
              <Modal.Content>
                {reviewer && (
                  <div className="member-list">
                    <h4>{i18next.t("Member Emails")}</h4>
                    {reviewer.members && reviewer.members.length > 0 ? (
                      <List>
                        {reviewer.members.map((member, index) => (
                          <List.Item key={index}>
                            <Icon name="mail" />
                            <List.Content>{member.email}</List.Content>
                          </List.Item>
                        ))}
                      </List>
                    ) : (
                      <p>{i18next.t("No members found.")}</p>
                    )}
                  </div>
                )}
              </Modal.Content>

              <Modal.Content>
                <Form className="full-width">
                  <Form.Field>
                    <TextAreaField
                      required
                      fieldPath="emails"
                      label={i18next.t("Add member email(s)")}
                      placeholder={i18next.t("Enter email addresses, separated by commas or new lines...")}
                      fluid
                    />
                  </Form.Field>
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button onClick={this.props.onClose} floated="left">
                  {i18next.t("Close")}
                </Button>
                <Button
                  size="small"
                  labelPosition="left"
                  icon="plus"
                  color="green"
                  content={i18next.t("Add member")}
                  onClick={(event) => handleSubmit(event)}
                  loading={loading}
                  disabled={loading}
                />
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
  isRecord: PropTypes.bool,
};

MemberAction.defaultProps = {
  isRecord: false,
};

