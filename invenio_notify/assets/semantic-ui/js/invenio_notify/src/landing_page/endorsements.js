/*
 * Copyright (C) 2025-2026 Cottage Labs.
 *
 * Invenio-Notify is free software; you can redistribute it and/or modify
 * it under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import { EndorsementsDisplay } from "./EndorsementsDisplay";

const recordEndorsementDisplayDiv = document.getElementById("recordEndorsementDisplay");

if (recordEndorsementDisplayDiv) {
    const record = JSON.parse(recordEndorsementDisplayDiv.dataset.record);
    ReactDOM.render(
        <EndorsementsDisplay record={record} />,
        recordEndorsementDisplayDiv
    );
}