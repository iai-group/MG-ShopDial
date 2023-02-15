"""Class with available topics for the experiment."""

import dataclasses
import json
import random
from typing import Dict, List

import yaml


@dataclasses.dataclass
class Scenario:
    id: int
    desc: str
    type: str
    constraint: str

    def __iter__(self):
        yield from {
            "id": self.id,
            "desc": self.desc,
            "type": self.type,
            "constraint": self.constraint,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()


@dataclasses.dataclass
class Topics:
    topics: Dict[str, List[Scenario]] = dataclasses.field(default_factory=dict)
    used_scenarios: Dict[int, List[Scenario]] = dataclasses.field(
        default_factory=dict
    )

    def create_scenario_pool(self, n: int = 50) -> None:
        """Sets up a scenario pool per topic.

        Args:
            n: Number of scenarios per topic.
        """
        for topic, scenarios in self.topics.items():
            nb_unique_scenarios = len(scenarios)
            r, q = divmod(n, nb_unique_scenarios)
            duplicated_scenarios = list()
            for i, scenario in enumerate(scenarios * r + [scenarios[-1]] * q):
                scenario.id = i
                duplicated_scenarios.append(scenario)
            self.topics[topic] = duplicated_scenarios

    def add_scenario(self, topic: str, scenario: Scenario) -> None:
        self.topics[topic] = self.topics[topic].append(scenario)

    def add_topic(self, topic: str, scenarios: List[Scenario] = []) -> None:
        self.topics[topic] = scenarios

    def get_topic_categories(self) -> List[str]:
        return list(self.topics.keys())

    def get_random_scenario(self, topic: str) -> Scenario:
        """Returns a random scenario for a selected topic.

        Args:
            topic: Selected topic.

        Returns:
            Random scenario.

        Raises:
            IndexError: If all scenario for topic were consumed
        """
        if not self.have_scenario(topic):
            raise IndexError(f"No more scenario for {topic}.")
        scenarios = self.topics[topic]
        i = random.choice(range(0, len(scenarios)))
        scenario = scenarios.pop(i)
        self.topics[topic] = scenarios
        self.used_scenarios[topic] = self.used_scenarios.get(topic, []) + [
            scenario
        ]

        return scenario

    def get_scenario(self, topic: str, scenario_id: int) -> Scenario:
        """Returns a scenario based on its id.

        Args:
            topic: Selected topic.
            scenario_id: Scenario id.

        Returns:
            Scenario.
        """
        for scenario in self.used_scenarios.get(topic, []):
            if scenario.id == scenario_id:
                return scenario
        return None

    def have_scenario(self, topic: str) -> bool:
        """Returns if topic has scenario.

        Args:
            topic: Selected topic.

        Returns:
            Whether all scenario were consumed.
        """
        if not self.topics[topic]:
            return False
        return True


def load_topics(filepath: str, n: int = 50) -> Topics:
    """Loads topics from YAML file.

    Args:
        filepath: Path to YAML file.
        n: Number of scenario per topic.

    Returns:
        List of available topics for the experiment.
    """
    topics = Topics()
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)

    i = 0
    for topic, scenarios in data.items():
        s = list()
        for scenario in scenarios:
            scenario["id"] = i
            s.append(Scenario(**scenario))
            i += 1
        topics.add_topic(topic, s)

    topics.create_scenario_pool(n)

    return topics
