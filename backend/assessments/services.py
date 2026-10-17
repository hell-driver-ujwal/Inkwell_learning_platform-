"""Confidence ratings are self reports, not knowledge test scores."""

from decimal import Decimal

from rest_framework.exceptions import ValidationError


def assess_ratings(*, statements, ratings):
    """Require every statement exactly once and return the original feedback bands."""
    expected = {statement.id for statement in statements}
    actual = [rating["statement_id"] for rating in ratings]
    if not expected or set(actual) != expected or len(actual) != len(expected):
        raise ValidationError("Rate every statement exactly once.")
    if any(type(entry["rating"]) is not int or not 1 <= entry["rating"] <= 5 for entry in ratings):
        raise ValidationError("Each rating must be an integer from one to five.")
    average = sum(Decimal(rating["rating"]) for rating in ratings) / len(ratings)
    if average < Decimal("2.5"):
        level = "Needs Improvement"
        feedback = "Review this topic and practise the key concepts before moving on."
    elif average < 4:
        level = "Developing"
        feedback = (
            "You have some confidence, but more practice would strengthen your understanding."
        )
    else:
        level = "Confident"
        feedback = "Continue practising to maintain and apply your understanding."
    return {"average": str(average.quantize(Decimal("0.01"))), "level": level, "feedback": feedback}
