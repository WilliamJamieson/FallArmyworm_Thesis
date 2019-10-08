import datetime
import sys

import crane.crane_sim_50_gen_0_bt_ad_libitum.simulator as run_sim


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_number = sys.argv[1]
    else:
        run_number = 0

    elapsed_time = run_sim.run_simulation(run_number)
    print('{} Run {} Has completed after {} of running'.
          format(datetime.datetime.now(),
                 run_number,
                 elapsed_time))
