/*
 * Copyright (C) 2025-2026 Cottage Labs.
 *
 * Invenio-Notify is free software; you can redistribute it and/or modify
 * it under the terms of the MIT License; see LICENSE file for more details.
 */

import { withCancel, http } from "react-invenio-forms";

// Global versions store to share data across multiple React trees
class VersionsStore {
    constructor() {
        this.subscribers = new Set();
        this.state = {
            allVersions: {},
            versionsLoading: true,
            versionsError: null,
        };
        this.fetchPromise = null;
        this.currentRecord = null;
    }

    subscribe(callback) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    getState() {
        return this.state;
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.subscribers.forEach(callback => callback(this.state));
    }

    async fetchVersions(record) {
        // Return existing promise if already fetching for the same record
        if (this.fetchPromise && this.currentRecord?.id === record?.id) {
            return this.fetchPromise;
        }

        // If record changed, reset state
        if (this.currentRecord?.id !== record?.id) {
            this.setState({
                allVersions: {},
                versionsLoading: true,
                versionsError: null,
            });
        }

        this.currentRecord = record;

        if (!record || !record.links || !record.links.versions) {
            this.setState({
                versionsLoading: false,
                versionsError: "No versions link available",
            });
            return Promise.resolve();
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
        this.fetchPromise = cancellableFetch.promise;

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

                this.setState({
                    allVersions: { hits, total },
                    versionsLoading: false,
                });
            })
            .catch((error) => {
                if (error !== "UNMOUNTED") {
                    this.setState({
                        versionsError: "An error occurred while fetching the versions.",
                        versionsLoading: false,
                    });
                }
            });

        return this.fetchPromise;
    }
}

// Export singleton instance
export const versionsStore = new VersionsStore();