from lib import APIParser
from lib.highlighter import print_init, print_info, print_err, print_info_2, print_update_info, print_up_to_date
from requests import post
from lib.utils import get_api_data, match_series, timer, get_only_chapter_number
import sys
from time import sleep
from datetime import datetime
from fspy import FlareSolverr
from fspy.solver_exceptions import FlareSolverError
import gc
import multiprocessing
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config = config['DEFAULT']

API = config["APIBase"]
print_init(f"API IP set to: {API}")

API_URL = f"{API}/series/get"
POST_URL = f"{API}/series/update/manga/"

FLARE_SOLVERR_SESSION_NAME = config["FlareSolverSessionName"]


@timer
def main(rq):
    print_init("Setting up FlareSolverr...")
    initialize_solver = FlareSolverr()
    if FLARE_SOLVERR_SESSION_NAME not in initialize_solver.sessions:
        initialize_solver.create_session(session_id=FLARE_SOLVERR_SESSION_NAME)
        print_init(f"Created FlareSolverr session: {FLARE_SOLVERR_SESSION_NAME}")

    print_init("Requesting API Data...")
    data = get_api_data(API_URL)

    print_init("Parsing series...")
    series = APIParser.parse_api_json(data)
    del data

    print_init("Matching series with settings...")
    match_series(series)

    for ser in series:
        try:
            payload = {"id": ser.id}
            last_ch_data = ser.setting.func(ser.base_url, ser.setting.xpath_chapter[0], ser.setting.xpath_url[0])

            source_last_ch_num = get_only_chapter_number(last_ch_data[0])
            source_last_ch_url = last_ch_data[1]

            base_last_ch_num = get_only_chapter_number(ser.setting.base(ser.base_url))

            if ser.source_chap != float(source_last_ch_num):
                payload["source_chap"] = source_last_ch_num
                payload["time2"] = ser.time1
                payload["time1"] = datetime.now().strftime("%d/%m/%Y - %H.%M")
            if ser.base_chap != float(base_last_ch_num):
                payload["base_chap"] = base_last_ch_num
            if ser.last_chapter_url != source_last_ch_url:
                payload["last_chapter_url"] = source_last_ch_url

            if len(payload) > 1:
                update_response = post(POST_URL, json=payload)

                if update_response.status_code != 200:
                    print_err(
                        "Request failed while updating series! Status code: " +
                        f"{update_response.status_code}\n{payload}\n {update_response.text}" 
                    )
                    update_response.close()
                    continue

                print_update_info(ser.id, ser.name, f"UPDATED! [SRC({ser.source_chap} -> {source_last_ch_num}), BASE({ser.base_chap} -> {base_last_ch_num})]")
                update_response.close()
                del update_response
            else:
                print_up_to_date(ser.id)

            del base_last_ch_num
            del source_last_ch_url
            del source_last_ch_num
            del last_ch_data
            del payload
        except Exception as e:
            print_err(
                    str(e) + f" ID: {ser.id}"
                )
            continue
    gc.collect()
    try:
        initialize_solver.destroy_session(session_id=FLARE_SOLVERR_SESSION_NAME)
        print_info(f"Closed FlareSolverr session: {FLARE_SOLVERR_SESSION_NAME}")
    except FlareSolverError:
        pass
    rq.put(True)


if __name__ == "__main__":
    print_info("Press CTRL + C to exit.")

    INTERVAL = config["interval"]
    print_info_2("Interval set to: ", str(INTERVAL))

    try:
        while True:

            try:
                results_queue = multiprocessing.Queue()
                parse_process = multiprocessing.Process(target=main, args=(results_queue,))
                parse_process.daemon = True
                parse_process.start()
                result = results_queue.get()    # blocks until results are available
                parse_process.terminate()
            except Exception as e:
                print_err(
                    str(e)
                )

            print_info("Sleeping...")
            sleep(INTERVAL)
    except KeyboardInterrupt:
        solver = FlareSolverr()
        if FLARE_SOLVERR_SESSION_NAME in solver.sessions:
            solver.destroy_session(FLARE_SOLVERR_SESSION_NAME)
            print_info(f"Closed FlareSolverr session: {FLARE_SOLVERR_SESSION_NAME}")
        sys.exit()
