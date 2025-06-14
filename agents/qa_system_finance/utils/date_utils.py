"""
Date utility functions for the Financial QA System.

This module provides helper functions for date manipulations, such as
calculating the Monday of a specific week based on an offset from the current week.
"""
import datetime

def get_monday_of_week(week_offset: int) -> str:
    """
    Calculates the date of the Monday for a specific week, offset from the current week.

    The calculation is based on the current date. The offset determines which week's
    Monday to return (e.g., 0 for the current week's Monday, 1 for last week's Monday).

    Args:
        week_offset: An integer representing the number of weeks to offset from the
                     current week.
                     0 means the Monday of the current week.
                     1 means the Monday of the previous week.
                     And so on for non-negative integers.

    Returns:
        A string representing the date of the target Monday in "YYYY-MM-DD" format.
    """
    # Get today's date
    today = datetime.date.today()

    # Calculate the number of days to subtract to get to the current week's Monday.
    # today.weekday() returns 0 for Monday, 1 for Tuesday, ..., 6 for Sunday.
    days_to_subtract_for_current_monday = datetime.timedelta(days=today.weekday())

    # Get the date of the Monday of the current week
    current_week_monday = today - days_to_subtract_for_current_monday

    # Calculate the Monday of the target week by subtracting the offset in weeks.
    # Each week has 7 days, so timedelta(weeks=offset) works.
    target_monday = current_week_monday - datetime.timedelta(weeks=week_offset)

    # Return the date formatted as a string
    return target_monday.strftime("%Y-%m-%d")

if __name__ == '__main__':
    # Example usage for testing the function directly
    print("Illustrative examples for get_monday_of_week():")
    print(f"Monday of the current week (offset 0): {get_monday_of_week(0)}")
    print(f"Monday of last week (offset 1): {get_monday_of_week(1)}")
    print(f"Monday of two weeks ago (offset 2): {get_monday_of_week(2)}")

    # Example to show how it works if today is a specific day
    # Assume today is Wednesday, July 24, 2024.
    # today.weekday() would be 2.
    # days_to_subtract = 2 days.
    # current_week_monday = July 24 - 2 days = July 22, 2024.
    # get_monday_of_week(0) -> "2024-07-22"
    # get_monday_of_week(1) -> "2024-07-15" (July 22 - 7 days)
    # This matches expectations.
