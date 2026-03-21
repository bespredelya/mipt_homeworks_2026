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


def checks_date_parts(parts: list[str]) -> tuple[int, int, int] | None:
    if not all(part.isdigit() for part in parts):
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    if not (1 <= month <= MONTHS_IN_YEAR):
        return None
    max_days = get_days_in_month(month, year)
    if not (1 <= day <= max_days):
        return None
    return day, month, year


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    consist_of = maybe_dt.split("-")
    if len(consist_of) != DATE_PARTS_COUNT:
        return None
    return checks_date_parts(consist_of)


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


def is_same_month(
        parsed_date: tuple[int, int, int],
        day: int,
        month: int,
        year: int,
) -> bool:
    return (
        parsed_date[2] == year
        and parsed_date[1] == month
        and parsed_date[0] <= day
    )


def income_stats(day: int, month: int, year: int) -> tuple[float, float]:
    income = 0
    this_month_income = 0
    for date, amount in INCOME_MASSIVE:
        income_date = extract_date(date)
        if income_date is None:
            continue
        if check_date(income_date, (day, month, year)):
            income += amount
        if is_same_month(income_date, day, month, year):
            this_month_income += amount
    return income, this_month_income


def add_category(
        categories: dict[str, float],
        category: str,
        amount: float,
) -> None:
    if category not in categories:
        categories[category] = 0
    categories[category] += amount


def get_cost_values(
        elem: list[Any],
        date_stats: tuple[int, int, int],
        categories: dict[str, float],
) -> tuple[float, float]:
    parsed_date = extract_date(elem[0])
    if parsed_date is None:
        return 0, 0
    total_cost = 0
    month_cost = 0
    if check_date(parsed_date, date_stats):
        total_cost += elem[2]
    if is_same_month(parsed_date, date_stats[0], date_stats[1], date_stats[2]):
        month_cost += elem[2]
        add_category(categories, elem[1], elem[2])
    return total_cost, month_cost

def cost_stats(
        day: int,
        month: int, year: int, ) -> tuple[float, float, dict[str, float]]:
    cost = 0
    this_month_cost = 0
    categories: dict[str, float] = {}
    for elem in COST_MASSIVE:
        cost_values = get_cost_values(
            elem,
            (day, month, year),
            categories,
        )
        cost += cost_values[0]
        this_month_cost += cost_values[1]
    return cost, this_month_cost, categories


def get_profit_line(maybe_profit: float) -> str:
    if maybe_profit >= 0:
        return f"This month, the profit amounted to {maybe_profit:.2f} rubles."
    return f"This month, the loss amounted to {abs(maybe_profit):.2f} rubles."


def add_categories_to_answer(
        answer: list[str],
        categories: dict[str, float],
) -> None:
    sorted_categories = sorted(categories.keys())
    for index, category in enumerate(sorted_categories, start=1):
        amount = categories[category]
        answer.append(f"{index}. {category}: {amount_check(amount)}")


def stats_response(
        date: str,
        money_stats: tuple[float, float, float, float],
        categories: dict[str, float],
) -> str:
    answer = []
    answer.append(f"Your statistics as of {date}:")
    answer.append(f"Total capital: {money_stats[0]:.2f} rubles")
    answer.append(get_profit_line(money_stats[1]))
    answer.append(f"Income: {money_stats[2]:.2f} rubles")
    answer.append(f"Expenses: {money_stats[3]:.2f} rubles")
    answer.append("")
    answer.append("Details (category: amount):")
    add_categories_to_answer(answer, categories)
    return "\n".join(answer)


def stats_handler(report_date: str) -> str:
    our_date = extract_date(report_date)
    if our_date is None:
        return INCORRECT_DATE_MSG
    income_data = income_stats(*our_date)
    cost_data = cost_stats(*our_date)
    money_stats = (
        income_data[0] - cost_data[0],
        income_data[1] - cost_data[1],
        income_data[1],
        cost_data[1],
    )
    return stats_response(report_date, money_stats, cost_data[2])


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


def validate_cost_data(
        category: str,
        amount_str: str,
        date: str,
) -> str | None:
    if category_handler(category) is None:
        categories = cost_categories_handler()
        return f"{NOT_EXISTS_CATEGORY}\n{categories}"
    if is_correct_number(amount_str):
        pass
    else:
        return NONPOSITIVE_VALUE_MSG
    amount = float(amount_str)
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if extract_date(date) is None:
        return INCORRECT_DATE_MSG
    return None


def handle_cost_request(request: list[str]) -> str:
    if len(request) == STATS_COMMAND_LEN and request[1] == "categories":
        return cost_categories_handler()
    if len(request) == COST_COMMAND_LEN:
        category = request[1]
        amount_str = request[2].replace(",", ".")
        date = request[3]
        validation_error = validate_cost_data(category, amount_str, date)
        if validation_error is None:
            amount = float(amount_str)
            return cost_handler(category, amount, date)
        return validation_error
    return UNKNOWN_COMMAND_MSG


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
