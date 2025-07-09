import uuid


def payload_review(record_id, in_reply_to=None) -> dict:
    """Create notification data with a real record ID."""
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()

    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "context": {
            "id": f"https://127.0.0.1:5000/records/{record_id}"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
            "ietf:cite-as": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794#review-3136",
            "type": [
                "Page",
                "sorg:WebPage"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": [
            "Announce",
            "coar-notify:ReviewAction"
        ]
    }


def payload_endorsement_resp(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "context": {
            "id": f"https://127.0.0.1:5000/records/{record_id}"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "id": "https://evolbiol.peercommunityin.org/articles/rec?articleId=794",
            "ietf:cite-as": "https://doi.org/10.24072/pci.evolbiol.100794",
            "type": [
                "Page",
                "sorg:WebPage"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": [
            "Announce",
            "coar-notify:EndorsementAction"
        ]
    }


def payload_tentative_accept(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{in_reply_to}",
            "object": {
                "id": f"https://127.0.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been tentatively accepted, subject to further review.",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "TentativeAccept"
    }


def payload_reject(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{in_reply_to}",
            "object": {
                "id": f"https://127.0.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been rejected because...",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "Reject"
    }


def payload_tentative_reject(record_id, in_reply_to=None) -> dict:
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()
    
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "name": "Peer Community in Evolutionary Biology",
            "type": "Service"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",
        "object": {
            "actor": {
                "id": "https://orcid.org/0000-0002-1825-0097",
                "name": "Josiah Carberry",
                "type": "Person"
            },
            "id": f"urn:uuid:{in_reply_to}",
            "object": {
                "id": f"https://127.0.0.1:5000/records/{record_id}",
                "ietf:cite-as": "https://doi.org/10.5555/12345680",
                "ietf:item": {
                    "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                    "mediaType": "application/pdf",
                    "type": [
                        "Page",
                        "sorg:AboutPage"
                    ]
                },
                "type": "sorg:AboutPage"
            },
            "origin": {
                "id": "https://research-organisation.org/repository",
                "inbox": "https://research-organisation.org/inbox/",
                "type": "Service"
            },
            "target": {
                "id": "https://overlay-journal.com/system",
                "inbox": "https://overlay-journal.com/inbox/",
                "type": "Service"
            },
            "type": [
                "Offer",
                "coar-notify:EndorsementAction"
            ]
        },
        "origin": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "summary": "The offer has been tentatively rejected, subject to further review.",
        "target": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "type": "TentativeReject"
    }