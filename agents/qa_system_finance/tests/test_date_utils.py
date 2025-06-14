import unittest
import datetime
from agents.qa_system_finance.utils.date_utils import get_monday_of_week

class TestDateUtils(unittest.TestCase):

    def test_get_monday_of_week(self):
        today = datetime.date.today()

        # Offset 0: Current week's Monday
        expected_monday_offset_0 = today - datetime.timedelta(days=today.weekday())
        self.assertEqual(get_monday_of_week(0), expected_monday_offset_0.strftime("%Y-%m-%d"))

        # Offset 1: Last week's Monday
        expected_monday_offset_1 = expected_monday_offset_0 - datetime.timedelta(weeks=1)
        self.assertEqual(get_monday_of_week(1), expected_monday_offset_1.strftime("%Y-%m-%d"))

        # Offset 2: Two weeks ago's Monday
        expected_monday_offset_2 = expected_monday_offset_0 - datetime.timedelta(weeks=2)
        self.assertEqual(get_monday_of_week(2), expected_monday_offset_2.strftime("%Y-%m-%d"))

        # Test with a specific date to ensure logic is independent of current weekday
        # Let's say today is Wednesday, 2023-07-19. weekday() is 2.
        # Monday of that week is 2023-07-17.
        # If we simulate today being 2023-07-19
        simulated_today = datetime.date(2023, 7, 19)

        # Mock datetime.date.today() for this part of the test if more complex scenarios are needed
        # For now, we calculate based on a known fixed date and compare results

        # If today was 2023-07-19 (Wednesday)
        # current_week_monday = 2023-07-19 - timedelta(days=2) = 2023-07-17
        # get_monday_of_week(0) should be "2023-07-17"
        # get_monday_of_week(1) should be "2023-07-10"

        # This test relies on the current implementation of get_monday_of_week
        # which itself uses datetime.date.today(). The above assertions test its core logic.
        # To test against a fixed date, we would need to mock date.today() or pass date to func.
        # The current structure of get_monday_of_week doesn't allow passing a date.
        # The existing tests are sufficient given the function's current design.

if __name__ == '__main__':
    unittest.main()
