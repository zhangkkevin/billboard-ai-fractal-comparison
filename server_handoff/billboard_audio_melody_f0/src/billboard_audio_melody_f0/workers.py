from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from typing import Any, Callable, Iterable, List, TypeVar

from tqdm import tqdm

T = TypeVar("T")
R = TypeVar("R")


def run_pool_map(
    worker: Callable[[T], R],
    tasks: Iterable[T],
    workers: int,
    *,
    maxtasksperchild: int | None = None,
    desc: str = "Processing",
) -> List[R]:
    task_list = list(tasks)
    if not task_list:
        return []

    if maxtasksperchild is not None:
        with Pool(processes=workers, maxtasksperchild=maxtasksperchild) as pool:
            return list(tqdm(pool.imap_unordered(worker, task_list), total=len(task_list), desc=desc))

    results: List[R] = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(worker, t) for t in task_list]
        for fut in tqdm(as_completed(futures), total=len(futures), desc=desc):
            results.append(fut.result())
    return results
