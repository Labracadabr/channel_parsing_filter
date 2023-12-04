from web_interface import do_task
import time


# https://t.me/antalia_sales/806483
cycle = 0
while True:
    cycle += 1
    do_task('antalia_sales')
    print('done cycle', cycle)
    time.sleep(10*60)
