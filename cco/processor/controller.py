#
# cco.processor.controller
#

from logging import getLogger

logger = getLogger('cco.processor.controller')


def loop(jobname, fct, data, skip=0, limit=None, 
         bsize=10, action=None):
    logger.info('loop %s starting' % jobname)
    result = dict(count=0, created=0, updated=0, error=0)
    if skip > 0:
        start = skip - 1
        for i, row in enumerate(data):
            if i >= start:
                break
    for row in data:
        r = fct(row)
        #result['count'] += 1
        #if r is not None:
        #    result[r['info']] += 1
        update_counters(result, r)
        if result['count'] % bsize == 0:
            logger.info('loop %s: %s' % (jobname, result))
            if action is not None:
                action()
        if limit and result['count'] >= limit:
            break
    if action is not None:
        action()
    logger.info('loop %s finished: %s' % (jobname, result))
    return result

def update_counters(result, msg):
    result['count'] += 1
    if msg is None:
        return
    if isinstance(msg, dict):
        info = msg.get('info')
        if info == 'error':
            result['error'] += 1
            return
        key = msg['action'] + 'd'
        if key in result:
            result[key] += 1
    else:
        result[msg] += 1
