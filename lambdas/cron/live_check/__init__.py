import json
import logging

from cron.live_check.logic import parse_account_index
from cron.live_check.service import Deps, run
from shared import middleware

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
def handler(event, _context):
    stats = run(parse_account_index(event), Deps.default())
    return {"statusCode": 200, "body": json.dumps(stats.to_dict())}
