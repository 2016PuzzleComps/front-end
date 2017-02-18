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
        loc = self.expected_s(p, t)
        return norm.pdf(s, self.norm_spread, loc)

    @staticmethod
    def function_to_minimize(t, mle, ss, ps):
        ret = 1.0
        for s, p in zip(ss, ps):
            ret *= mle.conditional_pdf(s, p, t)
        return -ret

    def get_new_true_skill(self, old_t, solve_scores, puzzle_scores):
        result = minimize(self.function_to_minimize, old_t, args=(self, solve_scores, puzzle_scores), method='Nelder-Mead')
        print(result)
        return result.x[0]


if __name__ == '__main__':
    m = MLE(10, 1)
    result = m.get_new_true_skill(1, [1], [1])
    print(result)
    print(result.x)
    print(type(result))
