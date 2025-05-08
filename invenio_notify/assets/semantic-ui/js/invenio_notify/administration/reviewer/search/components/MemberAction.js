import { ActionModal, NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { ErrorMessage, http, TextAreaField, withCancel } from "react-invenio-forms";
import { Button, Form, Icon, List, Modal } from "semantic-ui-react";
import * as Yup from "yup";

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
      members: [],
      loadingMembers: false,
    };

    this.emailSchema = Yup.object({
      emails: Yup.string().required(i18next.t("Email is required")),
    });
  }

  componentDidMount() {
    if (this.state.reviewer) {
      this.fetchMembersList();
    }
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
    this.cancellableFetch && this.cancellableFetch.cancel();
  }

  componentDidUpdate(prevProps) {
    // Update state if reviewer prop changes
    if (prevProps.reviewer !== this.props.reviewer) {
      this.setState({ reviewer: this.props.reviewer }, () => {
        this.fetchMembersList();
      });
    }
  }

  fetchMembersList = async () => {
    const { reviewer } = this.state;
    if (!reviewer) return;

    this.setState({ loadingMembers: true });
    
    const apiUrl = `/api/reviewer/${reviewer.id}/members`;
    
    this.cancellableFetch = withCancel(http.get(apiUrl));
    
    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ 
        members: response.data.hits || [],
        loadingMembers: false,
        error: undefined
      });
    } catch (error) {
      if (error === "UNMOUNTED") return;
      
      this.setState({
        loadingMembers: false,
        error: error?.response?.data?.message || error?.message
      });
      console.error("Failed to fetch members:", error);
    }
  };

  updateReviewer = (updatedReviewer) => {
    // KTODO should no longer save reviewer in state
    this.setState({ reviewer: updatedReviewer }, () => {
      this.fetchMembersList();
    });
  };

  static contextType = NotificationContext;

  deleteMember = async (memberId) => {
    // KTODO refactor deleteMember and handleSubmit error handling
    this.setState({ loading: true });

    const { addNotification } = this.context;
    const { actionSuccessCallback } = this.props;
    const { reviewer } = this.state;

    const apiUrl = `/api/reviewer/${reviewer.id}/member`;

    this.cancellableAction = withCancel(
      http.delete(apiUrl, {
        data: { user_id: memberId },
        headers: { 'Content-Type': 'application/json' }
      })
    );

    try {
      const response = await this.cancellableAction.promise;
      this.setState({ loading: false, error: undefined });

      addNotification({
        title: i18next.t("Success"),
        content: i18next.t("Member removed successfully"),
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
    const { error, loading, loadingMembers, members } = this.state;
    const { } = this.props;
    const { reviewer } = this.state; // KTODO remove reviewer from state ?

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
                    {loadingMembers ? (
                      <div className="ui active centered inline loader"></div>
                    ) : members && members.length > 0 ? (
                      <List divided verticalAlign="middle">
                        {members.map((member, index) => (
                          <List.Item key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <Button
                                icon="trash"
                                color="red"
                                size="tiny"
                                style={{ marginRight: '1em' }}
                                onClick={() => this.deleteMember(member.id)}
                                disabled={loading}
                                title={i18next.t("Delete member")}
                              />
                              <Icon name="mail" />
                              {member.email}
                            </div>
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
  reviewer: PropTypes.object.isRequired,
  actionSuccessCallback: PropTypes.func,
};

MemberAction.propTypes = {
  reviewer: PropTypes.object.isRequired,
};

