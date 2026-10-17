"""Weighted quiz scoring; correct answers only appear in the submitted review."""

from decimal import ROUND_HALF_UP, Decimal

from rest_framework.exceptions import ValidationError


def score_quiz(*, questions, answers):
    """Reject foreign options and duplicates; unanswered questions earn zero."""
    question_map = {question.id: question for question in questions}
    chosen = {}
    for answer in answers:
        question_id = answer["question_id"]
        if question_id not in question_map or question_id in chosen:
            raise ValidationError("Unknown or duplicate quiz question.")
        option_id = answer.get("option_id")
        valid_options = {option.id for option in question_map[question_id].options.all()}
        if option_id is not None and option_id not in valid_options:
            raise ValidationError("The option does not belong to this question.")
        chosen[question_id] = option_id
    total = sum(question.marks for question in questions)
    if not total:
        raise ValidationError("This quiz has no questions.")
    earned = 0
    review = []
    for question in questions:
        selected = chosen.get(question.id)
        correct_options = [option for option in question.options.all() if option.is_correct]
        if len(correct_options) != 1:
            raise ValidationError("This quiz has invalid answer keys.")
        correct = correct_options[0]
        if selected == correct.id:
            earned += question.marks
        review.append(
            {
                "question_id": question.id,
                "text": question.text,
                "marks": question.marks,
                "selected_option": selected,
                "correct_option": correct.id,
                "options": [
                    {"id": option.id, "text": option.text} for option in question.options.all()
                ],
            }
        )
    score = (Decimal(earned * 100) / total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return score, review
