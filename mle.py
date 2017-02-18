from math import e, pi
from scipy.optimize import minimize
from scipy.stats import norm

# maximum likelihood estimator
class MLE:
    def __init__(self, max_score, norm_spread):
        self.norm_spread = norm_spread
        self.max_score = max_score

    def expected_s(self, p, t):
        return self.max_score/(1 + e**(t-p)) 

    def conditional_pdf(self, s, p, t):
        loc = expected_s(p, t)
        return norm.pdf(s, self.norm_spread, loc)

    def function_to_minimize(self, t, ss, ps):
        ret = 1.0
        for s, p in izip(ss, ps):
            ret *= conditional_pdf(s, p, t)
        return -ret

    def get_new_true_skill(self, old_t, solve_scores, puzzle_scores):
        return minimize(function_to_minimize, old_t, args=[solve_scores, puzzle_scores], method='Nelder-Mead')
