CREW_DIR := rooted_and_rising_crew

.PHONY: run train test replay install

run:
	cd $(CREW_DIR) && crewai run

install:
	cd $(CREW_DIR) && crewai install

train:
	cd $(CREW_DIR) && crewai train

test:
	cd $(CREW_DIR) && crewai test

replay:
	cd $(CREW_DIR) && crewai replay
