import { combineReducers } from "redux";
import membersReducer from "./members";

/**
 * Root reducer that combines all reducers for the actor administration
 */
const rootReducer = combineReducers({
  members: membersReducer,
  // Add other reducers here as needed
});

export default rootReducer;