/*
 * Copyright (C) 2025-2026 Cottage Labs.
 *
 * Invenio-Notify is free software; you can redistribute it and/or modify
 * it under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { createContext, useContext, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { withCancel, http } from "react-invenio-forms";

const VersionsContext = createContext();

export const useVersions = () => {
    const context = useContext(VersionsContext);
    if (!context) {
        throw new Error("useVersions must be used within a VersionsProvider");
    }
    return context;
};

export const VersionsProvider = ({ record, children }) => {
    const [allVersions, setAllVersions] = useState({});
    const [versionsLoading, setVersionsLoading] = useState(true);
    const [versionsError, setVersionsError] = useState(null);

    useEffect(() => {
        if (!record || !record.links || !record.links.versions) {
            setVersionsLoading(false);
            setVersionsError("No versions link available");
            return;
        }

        const fetchVersions = async () => {
            return await http.get(
                `${record.links.versions}?size=1000&sort=version&allversions=true`,
                {
                    headers: {
                        Accept: "application/vnd.inveniordm.v1+json",
                    },
                    withCredentials: true,
                }
            );
        };

        const cancellableFetch = withCancel(fetchVersions());

        cancellableFetch.promise
            .then((result) => {
                let { hits, total } = result.data.hits;
                hits = hits.map(record => ({
                    id: record.id,
                    parent: record.parent,
                    parent_id: record.parent.id,
                    publication_date: record.ui.publication_date_l10n_medium,
                    version: record.ui.version,
                    links: record.links,
                    pids: record.pids,
                    new_draft_parent_doi: record.ui.new_draft_parent_doi,
                    index: record.versions.index,
                    is_latest: record.versions.is_latest,
                }));

                setAllVersions({ hits, total });
                setVersionsLoading(false);
            })
            .catch((error) => {
                if (error !== "UNMOUNTED") {
                    setVersionsError("An error occurred while fetching the versions.");
                    setVersionsLoading(false);
                }
            });

        return () => {
            cancellableFetch.cancel();
        };
    }, [record]);

    const value = {
        allVersions,
        versionsLoading,
        versionsError,
    };

    return (
        <VersionsContext.Provider value={value}>
            {children}
        </VersionsContext.Provider>
    );
};

VersionsProvider.propTypes = {
    record: PropTypes.object.isRequired,
    children: PropTypes.node.isRequired,
};