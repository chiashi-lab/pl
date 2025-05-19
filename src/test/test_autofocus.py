import os
import sys
import time
sys.path.append('../')
from driver.horiba import Symphony
from driver.sigmakoki import shutter
from driver.focus_adjuster_driver import Focus_adjuster
from main import autofocus
from logger import Logger
import config

def autofocus_test_Si(path):
    #autofocus test on Si
    exposuretime = 3
    logger = Logger(log_file_path=os.path.join(path, "log.txt"))

    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_config_savetofiles(path)
    symphony.set_exposuretime(exposuretime)
    logger.log(f"exposuretime:{exposuretime}")

    stime = time.time()
    objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)
    shut.open(2)
    start_height = autofocus(objective_lens=objective_lens, symphony=symphony, savedirpath=path, exposuretime=exposuretime, logger=logger, range_dense_search=100, range_sparse_search=400)
    logger.log(f"autofocus at start position:{start_height}")
    logger.log(f"focus take {time.time()-stime}")

if __name__ == "__main__":
    path = input("Please input the path to save the data: ").strip('"')
    autofocus_test_Si(path)
