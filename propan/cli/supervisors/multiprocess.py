from multiprocessing.context import SpawnProcess
from typing import Any, List, Tuple

from propan.cli.supervisors.basereload import BaseReload
from propan.log import logger
from propan.types import DecoratedCallable


class Multiprocess(BaseReload):
    def __init__(
        self,
        target: DecoratedCallable,
        args: Tuple[Any, ...],
        workers: int,
    ) -> None:
        super().__init__(target, args, None)

        self.workers = workers
        self.processes: List[SpawnProcess] = []

    def startup(self) -> None:
        logger.info(f"Started parent process [{self.pid}]")

        for _ in range(self.workers):
            process = self._start_process()
            logger.info(f"Started child process [{process.pid}]")
            self.processes.append(process)

    def shutdown(self) -> None:
        for process in self.processes:
            process.terminate()
            logger.info(f"Stopping child process [{process.pid}]")
            process.join()

        logger.info(f"Stopping parent process [{self.pid}]")
