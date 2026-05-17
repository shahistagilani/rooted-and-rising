CREW_DIR := rooted_and_rising_crew
PYTHON   := $(CREW_DIR)/.venv/bin/python
DB_PATH  := $(CREW_DIR)/data/rooted.db

.PHONY: run demo install train test replay reset-db db-shell

## Interactive parent session (live input, history from DB)
run:
	cd $(CREW_DIR) && crewai run

## Hardcoded demo run (no prompts — good for CI / smoke-testing)
demo:
	cd $(CREW_DIR) && $(PYTHON) -m rooted_and_rising_crew.main_demo

install:
	cd $(CREW_DIR) && crewai install

train:
	cd $(CREW_DIR) && crewai train

test:
	cd $(CREW_DIR) && crewai test

replay:
	cd $(CREW_DIR) && crewai replay

## Delete the database (start fresh)
reset-db:
	rm -f $(DB_PATH)
	@echo "Database reset. A fresh one will be created on next run."

## Open the database in the sqlite3 shell
db-shell:
	sqlite3 $(DB_PATH)
