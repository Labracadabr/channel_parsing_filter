from web_interface import do_task
import time

last_results = [x for x in range(4)]  # список последних id
cycle = 0
while True:
    # вспомнить последний пост
    with open('last_good_id', 'r') as f:
        msg_id = int(f.read())

    last_results.pop(0)
    last_results.append(msg_id)

    # если последний айди не меняется X поисков подряд - искать до упора
    if len(set(last_results)) == 1:
        far = True
    else:
        far = False

    cycle += 1
    do_task(channel='antalia_sales', msg_id=msg_id, far=far)
    print('done cycle', cycle)
    time.sleep(30*60)  # ждать 30 мин

# пример https://t.me/antalia_sales/806483
