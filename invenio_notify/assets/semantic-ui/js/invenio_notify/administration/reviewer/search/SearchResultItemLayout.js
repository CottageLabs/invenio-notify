import { BoolFormatter, Actions } from "@js/invenio_administration";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table, Dropdown, Icon, Button } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { AdminUIRoutes } from "@js/invenio_administration/src/routes";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { ReviewerSearchActions } from "./ReviewerSearchActions";


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
        <Table.Cell data-label={i18next.t("COAR ID")}>
          {result.coar_id}
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
          />
        </Table.Cell>
      </Table.Row>
    );
  }
}

// KTODO
// SearchResultItemComponent.propTypes = {
//   actions: PropTypes.object.isRequired,
//   currentQueryState: PropTypes.object.isRequired,
//   displayDelete: PropTypes.bool.isRequired,
//   displayEdit: PropTypes.bool.isRequired,
//   idKeyPath: PropTypes.string.isRequired,
//   listUIEndpoint: PropTypes.string.isRequired,
//   resourceName: PropTypes.string.isRequired,
//   result: PropTypes.object.isRequired,
//   title: PropTypes.string.isRequired,
//   updateQueryState: PropTypes.func.isRequired,
// };

SearchResultItemComponent.defaultProps = {};

export const SearchResultItemLayout = withState(SearchResultItemComponent);
