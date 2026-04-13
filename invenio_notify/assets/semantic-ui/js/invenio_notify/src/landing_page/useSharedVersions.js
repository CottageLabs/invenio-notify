/*
 * Copyright (C) 2025-2026 Cottage Labs.
 *
 * Invenio-Notify is free software; you can redistribute it and/or modify
 * it under the terms of the MIT License; see LICENSE file for more details.
 */

import { useEffect, useState } from "react";
import { versionsStore } from "./VersionsStore";

export const useSharedVersions = (record) => {
    const [state, setState] = useState(versionsStore.getState());

    useEffect(() => {
        // Subscribe to store updates
        const unsubscribe = versionsStore.subscribe(setState);

        // Fetch versions if not already loading/loaded for this record
        versionsStore.fetchVersions(record);

        return unsubscribe;
    }, [record]);

    return state;
};