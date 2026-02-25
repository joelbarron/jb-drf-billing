def create_checkout_session(*, user, payload):
    return {
        "ok": False,
        "message": "Stripe checkout adapter not implemented yet.",
        "payload": payload,
    }


def create_portal_session(*, user):
    return {"ok": False, "message": "Stripe portal adapter not implemented yet."}
