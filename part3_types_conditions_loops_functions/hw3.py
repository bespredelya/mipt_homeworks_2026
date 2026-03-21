#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

FEBRUARY = 2
DATE_PARTS_COUNT = 3
MONTHS_IN_YEAR = 12
ONE_PART_COUNT = 1
TWO_PARTS_COUNT = 2
INCOME_COMMAND_LEN = 3
COST_COMMAND_LEN = 4
STATS_COMMAND_LEN = 2
COST_MASSIVE = []
INCOME_MASSIVE = []

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
    "Other": ("Other",),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return 29
        return 28
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    return 30


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    consist_of = maybe_dt.split("-")
    if len(consist_of) != DATE_PARTS_COUNT:
        return None
    day = consist_of[0]
    month = consist_of[1]
    year = consist_of[2]
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return None
    month_t = int(month)
    year_y = int(year)
    day_y = int(day)
    if not (1 <= month_t <= MONTHS_IN_YEAR):
        return None
    max_days = get_days_in_month(month_t, year_y)
    if not (1 <= day_y <= max_days):
        return None
    return day_y, month_t, year_y


def is_correct_number(value: str) -> bool:
    if value.count(".") > 1:
        return False
    parts = value.split(".")
    if len(parts) == ONE_PART_COUNT:
        return parts[0].isdigit()
    if len(parts) == TWO_PARTS_COUNT:
        if parts[0] == "" or parts[1] == "":
            return False
        return parts[0].isdigit() and parts[1].isdigit()
    return False


def income_handler(amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({"amount": amount, "date": date})
    INCOME_MASSIVE.append([income_date, amount])
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if category_handler(category_name) is None:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": date})
    COST_MASSIVE.append([income_date, category_name, amount])
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = []
    for elem, values in EXPENSE_CATEGORIES.items():
        categories.extend(f"{elem}::{categorie}" for categorie in values)
    return "\n".join(categories)


def category_handler(category_name: str) -> tuple[str, str] | None:
    pieces = category_name.split("::")
    if len(pieces) != TWO_PARTS_COUNT:
        return None
    one_category = pieces[0]
    two_category = pieces[1]
    if one_category not in EXPENSE_CATEGORIES:
        return None
    if two_category not in EXPENSE_CATEGORIES[one_category]:
        return None
    return one_category, two_category


def amount_check(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    amount_str = str(amount)
    while amount_str[-1] == "0":
        amount_str = amount_str[:-1]
    if amount_str[-1] == ".":
        amount_str = amount_str[:-1]
    return amount_str


def check_date(
        current_date: tuple[int, int, int],
        date_stats: tuple[int, int, int],
) -> bool:
    return (current_date[2], current_date[1], current_date[0]) <= (
        date_stats[2],
        date_stats[1],
        date_stats[0],
    )


def income_stats(day: int, month: int, year: int) -> tuple[float, float]:
    income = 0
    this_month_income = 0
    date_stats = (day, month, year)
    for date, amount in INCOME_MASSIVE:
        income_date = extract_date(date)
        if income_date is None:
            continue
        if check_date(income_date, date_stats):
            income += amount
        if income_date[2] == year and income_date[1] == month and income_date[0] <= day:
            this_month_income += amount
    return income, this_month_income


def cost_stats(day: int, month: int, year: int) -> tuple[float, float, dict[str, float]]:
    cost = 0
    this_month_cost = 0
    categories: dict[str, float] = {}
    date_stats = (day, month, year)
    for cost_date, category, amount in COST_MASSIVE:
        parsed_date = extract_date(cost_date)
        if parsed_date is None:
            continue
        if check_date(parsed_date, date_stats):
            cost += amount
        if parsed_date[2] == year and parsed_date[1] == month and parsed_date[0] <= day:
            this_month_cost += amount
            if category not in categories:
                categories[category] = 0
            categories[category] += amount
    return cost, this_month_cost, categories


def stats_response(
        date: str,
        money_stats: tuple[float, float, float, float],
        categories: dict[str, float],
) -> str:
    balance, maybe_profit, this_month_income, this_month_cost = money_stats
    answer = []
    answer.append(f"Your statistics as of {date}:")
    answer.append(f"Total capital: {balance:.2f} rubles")
    if maybe_profit >= 0:
        answer.append(f"This month, the profit amounted to {maybe_profit:.2f} rubles.")
    else:
        answer.append(f"This month, the loss amounted to {abs(maybe_profit):.2f} rubles.")
    answer.append(f"Income: {this_month_income:.2f} rubles")
    answer.append(f"Expenses: {this_month_cost:.2f} rubles")
    answer.append("")
    answer.append("Details (category: amount):")
    sorted_categories = sorted(categories.keys())
    for index, category in enumerate(sorted_categories, start=1):
        amount = categories[category]
        answer.append("{}. {}: {}".format(index, category, amount_check(amount)))
    return "\n".join(answer)


def stats_handler(report_date: str) -> str:
    our_date = extract_date(report_date)
    if our_date is None:
        return INCORRECT_DATE_MSG
    income, this_month_income = income_stats(*our_date)
    cost, this_month_cost, categories = cost_stats(*our_date)
    return stats_response(
        report_date,
        (
            income - cost,
            this_month_income - this_month_cost,
            this_month_income,
            this_month_cost,
        ),
        categories,
    )


def handle_income_request(request: list[str]) -> str:
    if len(request) != INCOME_COMMAND_LEN:
        return UNKNOWN_COMMAND_MSG
    amount_str = request[1].replace(",", ".")
    date = request[2]
    if not is_correct_number(amount_str):
        return NONPOSITIVE_VALUE_MSG
    amount = float(amount_str)
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(date) is None:
        return INCORRECT_DATE_MSG
    return income_handler(amount, date)


def handle_cost_request(request: list[str]) -> str:
    result = UNKNOWN_COMMAND_MSG
    if len(request) == STATS_COMMAND_LEN and request[1] == "categories":
        result = cost_categories_handler()
    elif len(request) == COST_COMMAND_LEN:
        category = request[1]
        amount_str = request[2].replace(",", ".")
        date = request[3]
        if category_handler(category) is None:
            categories = cost_categories_handler()
            result = NOT_EXISTS_CATEGORY + "\n" + categories
        elif not is_correct_number(amount_str):
            result = NONPOSITIVE_VALUE_MSG
        else:
            amount = float(amount_str)
            if amount <= 0:
                return NONPOSITIVE_VALUE_MSG
            if extract_date(date) is None:
                return INCORRECT_DATE_MSG
            result = cost_handler(category, amount, date)
    return result


def handle_stats_request(request: list[str]) -> str:
    if len(request) != STATS_COMMAND_LEN:
        return UNKNOWN_COMMAND_MSG
    date = request[1]
    if extract_date(date) is None:
        return INCORRECT_DATE_MSG
    return stats_handler(date)


def response_to_request(request: list[str]) -> str:
    if len(request) == 0:
        return UNKNOWN_COMMAND_MSG
    activity = request[0]
    handlers = {
        "income": handle_income_request,
        "cost": handle_cost_request,
        "stats": handle_stats_request,
    }
    handler = handlers.get(activity)
    if handler is None:
        return UNKNOWN_COMMAND_MSG
    return handler(request)


def main() -> None:
    while True:
        line = input()
        if line == "":
            break
        request = line.split()
        print(response_to_request(request))


if __name__ == "__main__":
    main()

