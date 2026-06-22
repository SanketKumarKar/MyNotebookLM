"""Spaced repetition scheduler using Leitner-inspired intervals."""

from datetime import datetime, timedelta
from utils.logger import get_logger

log = get_logger("revision_scheduler")

# Leitner-inspired intervals (in days)
REVISION_INTERVALS = [1, 3, 7, 14, 30]


class RevisionScheduler:
    """Build spaced repetition revision schedules."""

    def create_schedule(
        self,
        topics: list[str],
        start_date: datetime | None = None,
        num_rounds: int = 5,
    ) -> list[dict]:
        """
        Create a revision schedule for the given topics.

        Each topic gets num_rounds revision sessions at Leitner intervals.

        Returns:
            List of dicts with keys: topic, session, date, interval_days
        """
        if start_date is None:
            start_date = datetime.now()

        schedule = []
        for topic in topics:
            for session_idx in range(min(num_rounds, len(REVISION_INTERVALS))):
                interval = REVISION_INTERVALS[session_idx]
                rev_date = start_date + timedelta(days=interval)
                schedule.append({
                    "topic": topic,
                    "session": session_idx + 1,
                    "date": rev_date.strftime("%Y-%m-%d"),
                    "interval_days": interval,
                    "priority": "high" if session_idx < 2 else "medium" if session_idx < 4 else "low",
                })

        # Sort by date, then by topic
        schedule.sort(key=lambda x: (x["date"], x["topic"]))
        log.info(f"Created revision schedule: {len(schedule)} sessions for {len(topics)} topics")
        return schedule

    def export_csv(self, schedule: list[dict]) -> str:
        """Export revision schedule as CSV string."""
        import io
        import csv

        output = io.StringIO()
        if not schedule:
            return "No revision schedule to export."

        writer = csv.DictWriter(output, fieldnames=["topic", "session", "date", "interval_days", "priority"])
        writer.writeheader()
        writer.writerows(schedule)
        return output.getvalue()
