
import time
import uuid

import sublime_plugin


TOUCH_EVENT_TIME = None
TOUCH_EVENT_HANDLERS = {}
TOUCH_EVENT_HANDLERS_ASYNC = {}


def add_event_handler(view, region, handler=None, handler_id=None, HANDLERS=TOUCH_EVENT_HANDLERS):
    if handler_id is None:
        handler_id = uuid.uuid4()
    HANDLERS.setdefault(view.id(), {})[handler_id] = [region, handler]
    return handler_id


def add_event_handler_async(view, region, handler, handler_id=None):
    return add_event_handler(view, region, handler, handler_id, TOUCH_EVENT_HANDLERS_ASYNC)


def add_event_handlers(view, regions, handlers, handler_ids=None, HANDLERS=TOUCH_EVENT_HANDLERS):
    handler_ids = [] if handler_ids is None else handler_ids
    for i in range(regions):
        if len(handler_ids) == i:
            handler_ids.append(None)
        handler_ids[i] = add_event_handler(view, regions[i], handlers[i], handler_ids[i], HANDLERS)
    return handler_ids


def add_event_handlers_async(view, regions, handlers, handler_ids=None):
    return add_event_handlers(view, regions, handlers, handler_ids, TOUCH_EVENT_HANDLERS_ASYNC)


def remove_event_handler(view, handler_id, HANDLERS=TOUCH_EVENT_HANDLERS):
    if view.id() in HANDLERS and handler_id in HANDLERS[view.id()]:
        del HANDLERS[view.id()][handler_id]
        return handler_id


def remove_event_handler_async(view, handler_id):
    return remove_event_handler(view, handler_id, TOUCH_EVENT_HANDLERS_ASYNC)


def remove_event_handlers(view, HANDLERS=TOUCH_EVENT_HANDLERS):
    if view.id() in HANDLERS:
        handler_ids = HANDLERS[view.id()].keys()
        del HANDLERS[view.id()]
        return handler_ids


def remove_event_handlers_async(view):
    return remove_event_handlers(view, TOUCH_EVENT_HANDLERS_ASYNC)


def event_handler(view, HANDLERS=TOUCH_EVENT_HANDLERS):
    global TOUCH_EVENT_TIME
    if not view.id() in HANDLERS:
        return None
    regions = view.sel()
    event_time = time.time()
    if len(regions) == 1 and regions[0].empty() and (
        TOUCH_EVENT_TIME is None or
        TOUCH_EVENT_TIME < event_time - 0.2
    ):
        point = regions[0].begin()
        TOUCH_EVENT_TIME = event_time

        view_handler_items = list(HANDLERS[view.id()].items())
        for handler_id, region_handler in view_handler_items:
            region, handler = region_handler
            if region.contains(point):
                handler(handler_id, view, region, point)


class LiveEventListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        event_handler(view)

    def on_selection_modified_async(self, view):
        event_handler(view, TOUCH_EVENT_HANDLERS_ASYNC)

    def on_close(self, view):
        remove_event_handlers(view)
        remove_event_handlers_async(view)
