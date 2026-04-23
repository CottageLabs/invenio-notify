/*
 * Copyright (C) 2025-2026 Cottage Labs.
 *
 * Invenio-Notify is free software; you can redistribute it and/or modify
 * it under the terms of the MIT License; see LICENSE file for more details.
 */

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