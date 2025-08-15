import numpy as np
from scipy.stats import norm

def calculate_grade_probability(current_marks, remaining_marks_possible, target_grade_min, target_grade_max):
    """
    Calculates the probability of a student reaching a certain grade.

    Args:
        current_marks (float): The student's current marks secured (out of 100).
        remaining_marks_possible (float): The remaining marks possible to achieve.
        target_grade_min (float): The minimum percentage for the target grade.
        target_grade_max (float): The maximum percentage for the target grade.

    Returns:
        float: The probability of the student reaching the target grade.
    """
    total_possible_marks = current_marks + remaining_marks_possible

    # If remaining_marks_possible is 0, the final mark is fixed
    if remaining_marks_possible == 0:
        if target_grade_min <= current_marks <= target_grade_max:
            return 1.0
        else:
            return 0.0

    # The final grade for the course is assumed to follow a normal distribution
    # with a mean of 55 and a standard deviation of 15.
    mean_final_grade = 55
    std_dev_final_grade = 15

    # Calculate the probability of the final grade falling within the target range
    prob_below_max = norm.cdf(target_grade_max, loc=mean_final_grade, scale=std_dev_final_grade)
    prob_below_min = norm.cdf(target_grade_min, loc=mean_final_grade, scale=std_dev_final_grade)

    probability = prob_below_max - prob_below_min
    return probability
