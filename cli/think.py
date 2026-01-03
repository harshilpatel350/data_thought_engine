"""
Command-line interface to trigger the Data Thought Engine pipeline.
Accepts a dataset path and optional storage directory.
"""
from __future__ import annotations

import argparse
from data_thought_engine.core.context import Context
from data_thought_engine.core.engine import run_pipeline
from data_thought_engine.ingestion.schema import infer_schema
from data_thought_engine.utils.logger import get_logger
from data_thought_engine.utils.checks import assert_path_exists, assert_is_csv


def cli_run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Data Thought Engine (DTE)')
    parser.add_argument('dataset', help='Path to CSV dataset file')
    args = parser.parse_args(argv)

    assert_path_exists(args.dataset)
    assert_is_csv(args.dataset)

    schema = infer_schema(args.dataset, max_rows=200)
    logger = get_logger('dte')
    ctx = Context(dataset_path=args.dataset, num_rows_sampled=0, schema=schema)
    logger.info('Starting DTE run', {'dataset': args.dataset})
    run_pipeline(ctx)
    logger.info('DTE run complete', {'dataset': args.dataset})


if __name__ == '__main__':
    cli_run()
