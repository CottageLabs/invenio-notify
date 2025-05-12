/*
 * for debugging purposes, TOBEREMOVED
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchFacets } from "@js/invenio_administration";
import PropTypes from "prop-types";
import React, { Component } from "react";
// import { UserStatusFilter } from "./filters";
import { SearchBar, Sort } from "react-searchkit";
import { Grid } from "semantic-ui-react";

export class PgUserSearchLayout extends Component {
  render() {
    const { config, appName } = this.props;
    return (
      <>
      <div>
        <h1>Yooooooooooooooooooooooooooooooo 4444444</h1>
      </div>

      </>
    );
  }
}

PgUserSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

PgUserSearchLayout.defaultProps = {
  appName: "",
};
