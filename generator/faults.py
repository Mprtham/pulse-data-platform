import random
import copy


FAULT_RATE = 0.15


def maybe_inject(event: dict) -> dict:
    if random.random() > FAULT_RATE:
        return event

    event = copy.deepcopy(event)
    fault = random.choice(["missing_invoice", "negative_price", "null_quantity", "duplicate_id"])

    if fault == "missing_invoice":
        event["invoice_no"] = None
    elif fault == "negative_price":
        event["unit_price"] = round(-abs(event["unit_price"]), 2)
    elif fault == "null_quantity":
        event["quantity"] = None
    elif fault == "duplicate_id":
        # caller must supply the last-seen invoice pool
        event["_force_duplicate"] = True

    return event
