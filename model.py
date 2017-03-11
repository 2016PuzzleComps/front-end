# puzzle data
min_wwl = 7.231 # Lowest value in db
max_wwl = 297.096 # Highest value in db
norm_spread = 94.288 # Average standard deviation of mturk data
min_expected_score = 5 # expected solve score on easiest puzzle
# correlation coefficients
wwl_coef = .531
puzzle_score_offset = 51.68
solve_score_formula = "weighted_walk_length * %s + %s" % (wwl_coef, puzzle_score_offset) # for db queries
def get_solve_score(wwl):
    return wwl * wwl_coef + puzzle_score_offset
# tuneables
ideal_score = 90

print(get_solve_score(39.14568))
