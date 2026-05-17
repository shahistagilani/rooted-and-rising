from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from .models import GapReport, JournalEntry, LibraryExtraction, WeeklyPlan

# Single shared LLM instance — set temperature low for structured JSON output
_LLM = LLM(model="anthropic/claude-haiku-4-5-20251001", temperature=0.2)


@CrewBase
class RootedAndRisingCrew:
    """Rooted and Rising — child growth co-pilot crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def journal_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["journal_agent"],  # type: ignore[index]
            llm=_LLM,
            verbose=True,
        )

    @agent
    def library_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["library_agent"],  # type: ignore[index]
            llm=_LLM,
            verbose=True,
        )

    @agent
    def balance_analyser(self) -> Agent:
        return Agent(
            config=self.agents_config["balance_analyser"],  # type: ignore[index]
            llm=_LLM,
            verbose=True,
        )

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["planner_agent"],  # type: ignore[index]
            llm=_LLM,
            verbose=True,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def journal_task(self) -> Task:
        return Task(
            config=self.tasks_config["journal_task"],  # type: ignore[index]
            output_pydantic=JournalEntry,
        )

    @task
    def library_task(self) -> Task:
        return Task(
            config=self.tasks_config["library_task"],  # type: ignore[index]
            output_pydantic=LibraryExtraction,
        )

    @task
    def balance_task(self) -> Task:
        return Task(
            config=self.tasks_config["balance_task"],  # type: ignore[index]
            output_pydantic=GapReport,
        )

    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],  # type: ignore[index]
            output_pydantic=WeeklyPlan,
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
