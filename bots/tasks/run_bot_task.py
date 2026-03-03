import logging
import os
import signal

from celery import shared_task
from celery.signals import worker_shutting_down

from bots.bot_controller import BotController

logger = logging.getLogger(__name__)


@shared_task(bind=True, soft_time_limit=3600)
def run_bot(self, bot_id):
    logger.info(f"Running bot {bot_id}")
    bot_controller = BotController(bot_id)
    bot_controller.run()


def kill_child_processes():
    # Get the process group ID (PGID) of the current process
    pgid = os.getpgid(os.getpid())

    try:
        # Send SIGTERM to all processes in the process group
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        pass  # Process group may no longer exist


_shutting_down = False

@worker_shutting_down.connect
def shutting_down_handler(sig, how, exitcode, **kwargs):
    global _shutting_down
    if _shutting_down:
        return
    _shutting_down = True
    logger.info("Celery worker shutting down, sending SIGTERM to all child processes")
    kill_child_processes()
