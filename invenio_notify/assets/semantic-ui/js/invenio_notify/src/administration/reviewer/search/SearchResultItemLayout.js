import { BoolFormatter, Actions } from "@js/invenio_administration";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table, Dropdown, Icon, Button } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { AdminUIRoutes } from "@js/invenio_administration/src/routes";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { ReviewerSearchActions } from "./ReviewerSearchActions";
import { Provider } from "react-redux";
import store from "./state/store";

class SearchResultItemComponent extends Component {

  render() {
    const {
      result,
      listUIEndpoint,
      idKeyPath,
      ...values
    } = this.props;

    return (
      <Table.Row>
        <Table.Cell key={`reviewer-Id-${result.id}`} data-label={i18next.t("Id")}>
          {result.id}
        </Table.Cell>
        <Table.Cell key={`reviewer-active-${result.id}`} data-label={i18next.t("Name")}>
          <a href={AdminUIRoutes.editView(listUIEndpoint, result, idKeyPath)} >
            {result.name}
          </a>
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Actor ID")}>
          {result.actor_id}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Inbox URL")}>
          {result.inbox_url}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Description")}>
          {result.description || "-"}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Created")}>
          {new Date(result.created).toLocaleString()}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Updated")}>
          {new Date(result.updated).toLocaleString()}
        </Table.Cell>
        <Table.Cell collapsing>
          <ReviewerSearchActions 
            result={result}
          />
        </Table.Cell>
      </Table.Row>
    );
  }
}

SearchResultItemComponent.defaultProps = {};

export const SearchResultItemLayout = withState(
  (props) => (
    <Provider store={store}>
      <SearchResultItemComponent {...props} />
    </Provider>
  )
);
