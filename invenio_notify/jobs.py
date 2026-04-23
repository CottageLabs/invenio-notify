#  Copyright (C) 2025-2026 Cottage Labs.
#
#  Invenio-Notify is free software; you can redistribute it and/or modify
#  it under the terms of the MIT License; see LICENSE file for more details.

from invenio_jobs.jobs import JobType

from invenio_notify import tasks


class ProcessNotifyInboxJob(JobType):
    """ Process notify inbox records job """

    task = tasks.shared_task_inbox_processing
    id = 'process_notify_inbox'
    title = 'Process notify inbox'
    description = 'Process notify inbox records'
