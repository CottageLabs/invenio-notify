import { Actions } from "@js/invenio_administration";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { AdminUIRoutes } from "@js/invenio_administration/src/routes";
import { i18next } from "@translations/invenio_app_rdm/i18next";

class SearchResultItemComponent extends Component {

  /**
   * Generate link to administration record page if recid exists
   */
  generateRecordLink = (recid) => {
    if (!recid) return "-";

    const recordUrl = `/administration/records?q=id:${recid}&f=allversions:true`;
    return (
      <a 
        href={recordUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="ui blue link"
        title={i18next.t("View record in administration")}
      >
        {recid}
        <i className="external alternate icon ml-5" />
      </a>
    );
  };

  /**
   * Truncate long text content with tooltip
   */
  truncateText = (text, maxLength = 100) => {
    if (!text) return "-";
    if (text.length <= maxLength) return text;
    
    return (
      <span title={text}>
        {text.substring(0, maxLength)}...
      </span>
    );
  };

  /**
   * Format date for display
   */
  formatDate = (dateString) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString();
  };

  render() {
    const {
      title,
      resourceName,
      result,
      displayEdit,
      displayDelete,
      actions,
      idKeyPath,
      listUIEndpoint,
      ...values
    } = this.props;

    return (
      <Table.Row>
        <Table.Cell key={`notification-id-${result.id}`} data-label={i18next.t("Id")}>
          <a href={AdminUIRoutes.detailsView(listUIEndpoint, result, idKeyPath)} >
            {result.id}
          </a>
        </Table.Cell>
        
        <Table.Cell key={`notification-notification_id-${result.id}`} data-label={i18next.t("Notification ID")}>
          {result.notification_id}
        </Table.Cell>
        
        <Table.Cell key={`notification-raw-${result.id}`} data-label={i18next.t("Raw")} className="eight wide">
          <div style={{ maxHeight: "100px", overflow: "auto" }}>
            <pre style={{ fontSize: "0.8em", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {this.truncateText(result.raw, 200)}
            </pre>
          </div>
        </Table.Cell>
        
        <Table.Cell key={`notification-recid-${result.id}`} data-label={i18next.t("Record ID")}>
          {this.generateRecordLink(result.recid)}
        </Table.Cell>
        
        <Table.Cell key={`notification-user_id-${result.id}`} data-label={i18next.t("User ID")}>
          {result.user_id || "-"}
        </Table.Cell>
        
        <Table.Cell key={`notification-process_date-${result.id}`} data-label={i18next.t("Process Date")}>
          {this.formatDate(result.process_date)}
        </Table.Cell>
        
        <Table.Cell key={`notification-process_note-${result.id}`} data-label={i18next.t("Process Note")}>
          {this.truncateText(result.process_note, 50)}
        </Table.Cell>
        
        <Table.Cell key={`notification-created-${result.id}`} data-label={i18next.t("Created")}>
          {this.formatDate(result.created)}
        </Table.Cell>
        
        <Table.Cell key={`notification-updated-${result.id}`} data-label={i18next.t("Updated")}>
          {this.formatDate(result.updated)}
        </Table.Cell>
        
        <Table.Cell collapsing>
          <Actions
            title={title}
            resourceName={resourceName}
            editUrl={AdminUIRoutes.editView(listUIEndpoint, result, idKeyPath)}
            displayEdit={displayEdit}
            displayDelete={displayDelete}
            actions={actions}
            resource={result}
            idKeyPath={idKeyPath}
            successCallback={this.refreshAfterAction}
            listUIEndpoint={listUIEndpoint}
          />
        </Table.Cell>
      </Table.Row>
    );
  }
}

SearchResultItemComponent.propTypes = {
  title: PropTypes.string,
  resourceName: PropTypes.string,
  result: PropTypes.object.isRequired,
  displayEdit: PropTypes.bool,
  displayDelete: PropTypes.bool,
  actions: PropTypes.object,
  idKeyPath: PropTypes.string,
  listUIEndpoint: PropTypes.string,
};

SearchResultItemComponent.defaultProps = {
  displayEdit: true,
  displayDelete: true,
};

export const SearchResultItemLayout = withState(SearchResultItemComponent);