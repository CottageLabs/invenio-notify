import { initDefaultSearchComponents } from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
// import { NotificationController, SearchResultItemLayout } from "@js/invenio_administration";
import { NotificationController} from "@js/invenio_administration";
import { SearchResultItemLayout } from "./search/SearchResultItemLayout";
import { UserSearchLayout } from "./search";
import { PgUserSearchLayout } from "./search";
import { SearchFacets } from "@js/invenio_administration";
// import { SearchBulkActionContext } from "./SearchBulkActionContext";

const domContainer = document.getElementById("invenio-search-config");

const defaultComponents = initDefaultSearchComponents(domContainer);


const overridenComponents = {
  ...defaultComponents,
  "InvenioAdministration.SearchResultItem.layout": SearchResultItemLayout,
//   "SearchApp.layout": PgUserSearchLayout,
};

createSearchAppInit(
  overridenComponents,
  true,
  "invenio-search-config",
  false,
  NotificationController
//     SearchBulkActionContext,
);
