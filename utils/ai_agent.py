# unibase/utils/ai_agent.py

import time
import threading
from unibase.utils import groq_integration, logger
from unibase.registry import get_connections
log = logger.get_logger()

class AIAgent:
    """
    An autonomous agent that monitors the UNIBASE registry and automates tasks.
    """
    def __init__(self, poll_interval=30):
        self.poll_interval = poll_interval  # seconds
        self.running = False

    def analyze_registry(self):
        """
        Analyze the registry and return suggestions.
        In a production system, this might call a sophisticated ML model.
        """
        registry = get_connections()
        suggestions = []
        for db_type, conns in registry.items():
            total_records = sum(len(conn["data"]) for conn in conns)
            if total_records > 10:
                suggestions.append(f"{db_type.upper()} has a large number of records. Consider indexing or migration.")
            else:
                suggestions.append(f"{db_type.upper()} looks good.")
        analysis = "\n".join(suggestions)
        ai_response = groq_integration.get_insights(f"Analyze registry summary:\n{analysis}")
        return ai_response

    def optimize_databases(self):
        """
        Simulate an optimization task.
        """
        log.info("AI Agent is optimizing databases...")
        return "Optimization complete. All systems are running at peak efficiency!"

    def run(self):
        """
        Start the agent loop in a separate thread.
        """
        self.running = True
        log.info("Starting AI Agent...")
        while self.running:
            suggestion = self.analyze_registry()
            log.info("AI Agent Suggestion:\n" + suggestion)
            optimization_status = self.optimize_databases()
            log.info(optimization_status)
            time.sleep(self.poll_interval)

    def stop(self):
        self.running = False
        log.info("AI Agent stopped.")

# Singleton instance for agent use.
agent_instance = AIAgent()
