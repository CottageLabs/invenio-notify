import { NotificationContext } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { ErrorMessage, TextAreaField } from "react-invenio-forms";
import { Button, Form, Icon, List, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import { fetchMembers, addMembers, deleteMember } from "../state/actions/members";

class MemberForm extends Component {
    constructor(props) {
        super(props);

        this.state = {
            loading: false,
            error: undefined,
        };

        this.emailSchema = Yup.object({
            emails: Yup.string().required(i18next.t("Email is required")),
        });
    }

    componentDidMount() {
        if (this.props.actorId) {
            this.fetchMembers(this.props.actorId);
        }
    }

    componentDidUpdate(prevProps) {
        // Update state if actorId prop changes
        if (prevProps.actorId !== this.props.actorId) {
            if (this.props.actorId) {
                this.fetchMembers(this.props.actorId);
            }
        }

        // Update members in state when Redux store is updated
        if (prevProps.members !== this.props.members) {
            this.setState({ members: this.props.members });
        }
    }

    fetchMembers = async (actorId) => {
        const { addNotification } = this.context;
        try {
            await this.props.fetchMembers(actorId);
        } catch (error) {
            addNotification({
                title: i18next.t("Error"),
                content: i18next.t("Unable to fetch members. {{error}}", {
                    error: error.errMessage || "Unknown error",
                }),
                type: "error",
            });
        }
    };

    static contextType = NotificationContext;

    handleMemberDelete = async (memberId) => {
        const { addNotification } = this.context;
        const { deleteMember, actorId, actionSuccessCallback } = this.props;

        try {
            await deleteMember(actorId, memberId);
        } catch (error) {
            addNotification({
                title: i18next.t("Error"),
                content: i18next.t("Unable to remove member. {{error}}", {
                    error: error.errMessage || "Unknown error",
                }),
                type: "error",
            });
        }

        addNotification({
            title: i18next.t("Success"),
            content: i18next.t("Member removed successfully"),
            type: "success",
        });

        if (actionSuccessCallback) {
            actionSuccessCallback();
        }
    };

    handleSubmit = async (values, { resetForm }) => {
        const { addNotification } = this.context;
        const { addMembers, actorId, actionSuccessCallback } = this.props;

        console.log("Submit member with email:", values.emails);

        const emails = values.emails
            .split(/[\s,]+/)
            .map(email => email.trim())
            .filter(email => email);

        console.log("Parsed email list:", emails);
        try {
            await addMembers(actorId, emails);
        } catch (error) {
            addNotification({
                title: i18next.t("Error"),
                content: i18next.t("Unable to add member. {{error}}", {
                    error: error.errMessage || "Unknown error",
                }),
                type: "error",
            });

            return
        }

        resetForm();

        addNotification({
            title: i18next.t("Success"),
            content: i18next.t("Added member {{member}}", {
                member: emails.join(", "),
            }),
            type: "success",
        });

        if (actionSuccessCallback) {
            actionSuccessCallback();
        }

    };

    initFormValues = () => {
        return {
            emails: "",
        };
    };

    render() {
        const { error, loading } = this.state;
        const { members, actorId } = this.props;

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
                                {actorId && (
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
                                                                onClick={() => this.handleMemberDelete(member.id)}
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
    actorId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    actionSuccessCallback: PropTypes.func,
    fetchMembers: PropTypes.func.isRequired,
    addMembers: PropTypes.func.isRequired,
    deleteMember: PropTypes.func.isRequired,
    members: PropTypes.array,
    loading: PropTypes.bool,
};

const mapStateToProps = (state) => ({
    members: state.members?.data || [],
});

const mapDispatchToProps = {
    fetchMembers,
    addMembers,
    deleteMember,
};

const MemberFormContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(MemberForm);

export { MemberForm, MemberFormContainer };
