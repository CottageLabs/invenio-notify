import { createStore, applyMiddleware, compose } from "redux";
import thunk from "redux-thunk";
import rootReducer from "./reducers";

/**
 * Configure the Redux store with middleware and dev tools
 * 
 * @param {Object} initialState - Initial state to initialize the store with
 * @returns {Object} Configured Redux store
 */
export const configureStore = (initialState = {}) => {
  const middleware = [thunk];
  
  // Enable Redux DevTools if available in browser
  const composeEnhancers =
    (typeof window !== "undefined" &&
      window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) ||
    compose;

  const store = createStore(
    rootReducer,
    initialState,
    composeEnhancers(applyMiddleware(...middleware))
  );

  return store;
};

/**
 * Create and configure a Redux store instance
 */
const store = configureStore();

export default store;