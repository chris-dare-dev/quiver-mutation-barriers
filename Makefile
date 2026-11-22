# Targets run from the repository root.
#   make test        fast tests: the core, the runner, the scheduler, the registry (under two minutes)
#   make test-slow   research/verify/smoke.py and the section batches, each computed afresh (several minutes)
#   make lint        ruff and mypy (neither is needed to run anything)
#   make build       the two C search programs, into build/
#   make smoke       the smoke batch, computed afresh, and the headline table of GUIDE.md from it
#   make plan BATCH=data/batches/section-07.toml    list what a run would compute, without computing
#   make run BATCH=data/batches/section-07.toml     compute the tasks of a batch that have no record yet
#   make report BATCH=data/batches/section-07.toml REPORT_ARGS=--full
#   make run BATCH=data/examples/own-quivers.toml   quivers of your own, as tasks (GUIDE.md); for one quiver,
#                                                   PYTHONPATH=src python3 -m qmb explore 3 -2 2 -1 3 -3
#   make record BATCH=data/batches/section-07.toml  run, then copy the records into data/records/ (committed code only)
#   make tables      write the generated tables of CLAIMS.md, GUIDE.md and data/claims/RECORDS.md
#   make check       fail if those tables are not what the registry and the records give
#   make expected DATA=research/experiments     rebuild data/claims/expected.json from the unpacked data archive
# ARGS is passed to the scheduler, for example ARGS="--workers 8 --memory-budget 16000".
PYTHON ?= python3
CC     ?= gcc
CFLAGS  = -O2 -Wall
BATCH  ?= data/batches/smoke.toml
ARGS   ?=
REPORT_ARGS ?=
DATA   ?= research/experiments

# the Python packages are under src/
export PYTHONPATH := $(CURDIR)/src

SCHEDULER = $(PYTHON) -m taskbatch
NAME      = $(basename $(notdir $(BATCH)))
RUN_DIR   = results/$(NAME)
SECTIONS  = section-05 section-07 section-08 section-09 section-10 section-12 section-14
CHECKED   = src/taskbatch src/qmb src/runners tests src/bookkeeping/adopt.py src/bookkeeping/claims.py src/bookkeeping/expected.py

.PHONY: test test-slow lint format build plan run report smoke record tables check expected

test:
	@$(MAKE) -s build || echo "no C compiler: the tests of the C back end are skipped"
	$(PYTHON) -m unittest discover -s tests -t .

test-slow: build
	$(PYTHON) -I research/verify/smoke.py
	rm -rf results/test-slow
	set -e; for name in $(SECTIONS); do \
		$(SCHEDULER) run data/batches/$$name.toml --out results/test-slow/$$name --quiet $(ARGS); \
	done

lint:
	ruff check $(CHECKED)
	ruff format --check $(CHECKED)
	mypy

format:
	ruff format $(CHECKED)

build: build/np_barrier build/np_qa_core

build/%: research/experiments/%.c
	@mkdir -p build
	$(CC) $(CFLAGS) -o $@ $<

plan:
	$(SCHEDULER) plan $(BATCH) $(ARGS)

run:
	$(SCHEDULER) run $(BATCH) $(ARGS)

report:
	$(SCHEDULER) report $(RUN_DIR) $(REPORT_ARGS)

smoke:
	rm -rf results/smoke
	$(SCHEDULER) run data/batches/smoke.toml --quiet $(ARGS)
	$(SCHEDULER) report results/smoke
	$(PYTHON) src/bookkeeping/claims.py headline results

record:
	$(SCHEDULER) run $(BATCH) $(ARGS)
	$(PYTHON) src/bookkeeping/claims.py adopt $(RUN_DIR)

tables:
	$(PYTHON) src/bookkeeping/claims.py tables

check:
	$(PYTHON) src/bookkeeping/claims.py check

expected:
	$(PYTHON) src/bookkeeping/expected.py build $(DATA)
