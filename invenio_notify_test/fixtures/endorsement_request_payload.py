import uuid


def payload_endorsement_request(record_id, in_reply_to=None) -> dict:
    # KTODO how to define value of object.ietf:item.id?
    # KTODO remember to update value of origin.id, origin.inbox when generating request
    if in_reply_to is None:
        in_reply_to = uuid.uuid4()

    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://coar-notify.net"
        ],
        "actor": {
            "id": "mailto:josiah.carberry@example.com",
            "name": "Josiah Carberry",
            "type": "Person"
        },
        "id": f"urn:uuid:{uuid.uuid4()}",
        "inReplyTo": f"urn:uuid:{in_reply_to}",  # TODO why endorsement request have inReplyTo
        "object": {
            "id":  f"https://127.0.0.1:5000/records/{record_id}",
            "ietf:cite-as": "https://doi.org/10.5555/12345680",
            "ietf:item": {
                "id": "https://research-organisation.org/repository/preprint/201203/421/content.pdf",
                "mediaType": "application/pdf",
                "type": [
                    "Article",
                    "sorg:ScholarlyArticle"
                ]
            },
            "type": [
                "Page",
                "sorg:AboutPage"
            ]
        },
        "origin": {
            "id": "https://research-organisation.org/repository",
            "inbox": "https://research-organisation.org/inbox/",
            "type": "Service"
        },
        "target": {
            "id": "https://evolbiol.peercommunityin.org/coar_notify/",
            "inbox": "https://evolbiol.peercommunityin.org/coar_notify/inbox/",
            "type": "Service"
        },
        "type": [
            "Offer",
            "coar-notify:EndorsementAction"
        ]
    }
