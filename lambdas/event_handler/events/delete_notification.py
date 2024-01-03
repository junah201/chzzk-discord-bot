try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

def handler(event, context):
    return {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": f"알림 삭제\n\n```{event.get('rawBody')}```",
        }
    }
