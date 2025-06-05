from invenio_jobs.jobs import JobType

from invenio_notify import tasks


class ProcessNotifyInboxJob(JobType):
    """ Process notify inbox records job """

    task = tasks.shared_task_inbox_processing
    id = 'process_notify_inbox'
    title = 'Process notify inbox'
    description = 'Process notify inbox records'
