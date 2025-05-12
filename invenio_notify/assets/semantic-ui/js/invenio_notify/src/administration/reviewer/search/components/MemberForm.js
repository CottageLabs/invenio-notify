import { NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { ErrorMessage, http, TextAreaField, withCancel } from "react-invenio-forms";
import { Button, Form, Icon, List, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import { getMembers } from "../state/actions/members";

class MemberForm extends Component {
  constructor(props) {
    super(props);

    // KTODO do we need to set reviewerId in state?
    this.state = {
      loading: false,
      error: undefined,
    };

    this.emailSchema = Yup.object({
      emails: Yup.string().required(i18next.t("Email is required")),
    });
  }

  componentDidMount() {
    if (this.props.reviewerId) {
      this.props.getMembers(this.props.reviewerId);
    }
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  componentDidUpdate(prevProps) {
    // Update state if reviewerId prop changes
    if (prevProps.reviewerId !== this.props.reviewerId) {
      this.fetchMembersList();
    }

    // Update members in state when Redux store is updated
    if (prevProps.members !== this.props.members) {
      this.setState({ members: this.props.members });
    }
  }

  fetchMembersList = async () => {
    const { reviewerId } = this.props;
    const { getMembers } = this.props;

    if (!reviewerId) return;

    await getMembers(reviewerId);
  };

  static contextType = NotificationContext;

  // KTODO replace this function with redux action
  deleteMember = async (memberId) => {
    // KTODO refactor deleteMember and handleSubmit error handling
    this.setState({ loading: true });

    const { addNotification } = this.context;
    const { actionSuccessCallback, reviewerId } = this.props;

    const apiUrl = `/api/reviewer/${reviewerId}/member`;

    this.cancellableAction = withCancel(
      http.delete(apiUrl, {
        data: { user_id: memberId },
        headers: { "Content-Type": "application/json" },
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

      this.fetchMembersList();

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

  // KTODO use redux action addMember
  handleSubmit = async (values, { resetForm }) => {
    this.setState({ loading: true });

    const { addNotification } = this.context;
    const { actionSuccessCallback, reviewerId } = this.props;

    const apiUrl = `/api/reviewer/${reviewerId}/members`;

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

      this.fetchMembersList();

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
    const { members, reviewerId } = this.props; 

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
                {reviewerId && (
                  <div className="member-list">
                    <h4>{i18next.t("Member Emails")}</h4>
                    {loading ? (
                      <div className="ui active centered inline loader"></div>
                    ) : members && members.length > 0 ? (
                      <List divided verticalAlign="middle">
                        {members.map((member, index) => (
                          <List.Item
                            key={index}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                            }}
                          >
                            <div>
                              <Button
                                icon="trash"
                                color="red"
                                size="tiny"
                                style={{ marginRight: "1em" }}
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
                      placeholder={i18next.t(
                        "Enter email addresses, separated by commas or new lines..."
                      )}
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
  reviewerId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  actionSuccessCallback: PropTypes.func,
  getMembers: PropTypes.func.isRequired,
  members: PropTypes.array,
  loading: PropTypes.bool,
};

const mapStateToProps = (state) => ({
  members: state.members?.data || [],
  loading: state.members?.loading || false,
});

const mapDispatchToProps = {
  getMembers,
};

const ConnectedMemberForm = connect(
  mapStateToProps,
  mapDispatchToProps
)(MemberForm);

export { MemberForm, ConnectedMemberForm };
