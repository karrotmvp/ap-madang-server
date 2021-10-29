from django.contrib.admin import DateFieldListFilter
from datetime import timedelta, date


class CustomDateFieldListFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)

        self.links = list(self.links)
        self.links.insert(
            1,
            (
                "어제",
                {
                    self.lookup_kwarg_since: str(yesterday),
                    self.lookup_kwarg_until: str(today),
                },
            ),
        )
        self.links.insert(
            3,
            (
                "내일",
                {
                    self.lookup_kwarg_since: str(today),
                    self.lookup_kwarg_until: str(tomorrow),
                },
            ),
        )
        self.links.insert(
            4,
            (
                "모레",
                {
                    self.lookup_kwarg_since: str(tomorrow),
                    self.lookup_kwarg_until: str(day_after_tomorrow),
                },
            ),
        )
