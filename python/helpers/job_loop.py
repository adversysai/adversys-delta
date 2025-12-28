import asyncio
from datetime import datetime
import time
from python.helpers.task_scheduler import TaskScheduler
from python.helpers.print_style import PrintStyle
from python.helpers import errors
from python.helpers import runtime, dotenv


SLEEP_TIME = 60

keep_running = True
pause_time = 0
rfc_warning_emitted = False


async def run_loop():
    global pause_time, keep_running, rfc_warning_emitted

    while True:
        if runtime.is_development():
            # Signal to container that the job loop should be paused
            # if we are runing a development instance to avoid duble-running the jobs
            rfc_password = dotenv.get_dotenv_value(dotenv.KEY_RFC_PASSWORD)
            if not rfc_password:
                if not rfc_warning_emitted:
                    PrintStyle().warning(
                        "RFC password not set; skipping development RFC pause. "
                        "Set RFC_PASSWORD in .env to enable RFC."
                    )
                    rfc_warning_emitted = True
            else:
                try:
                    await runtime.call_development_function(pause_loop)
                except Exception as e:
                    PrintStyle().error("Failed to pause job loop by development instance: " + errors.error_text(e))
        if not keep_running and (time.time() - pause_time) > (SLEEP_TIME * 2):
            resume_loop()
        if keep_running:
            try:
                await scheduler_tick()
            except Exception as e:
                PrintStyle().error(errors.format_error(e))
        await asyncio.sleep(SLEEP_TIME)  # TODO! - if we lower it under 1min, it can run a 5min job multiple times in it's target minute


async def scheduler_tick():
    # Get the task scheduler instance and print detailed debug info
    scheduler = TaskScheduler.get()
    # Run the scheduler tick
    await scheduler.tick()


def pause_loop():
    global keep_running, pause_time
    keep_running = False
    pause_time = time.time()


def resume_loop():
    global keep_running, pause_time
    keep_running = True
    pause_time = 0
