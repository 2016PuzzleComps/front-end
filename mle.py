from math import e, pi, log
from scipy.optimize import minimize
from scipy.stats import norm
import sys

# maximum likelihood estimator
class MLE:
    max_angle = 1000

    def __init__(self, max_score, norm_spread):
        self.norm_spread = norm_spread
        self.max_score = max_score

    def expected_s(self, p, t, angle):
        return self.max_score/(1 + e**((t-p)/angle)) 

    def expected_p(self, s, t, angle):
        return t - angle * log(self.max_score/s - 1)

    def conditional_pdf(self, s, p, t, angle):
        loc = self.expected_s(p, t, angle)
        return norm.pdf(s, self.norm_spread, loc)

    @staticmethod
    def function_to_minimize(x, mle, ss, ps):
        t, angle = x
        if angle > MLE.max_angle:
            return sys.maxint
        ret = 1.0
        for s, p in zip(ss, ps):
            ret *= mle.conditional_pdf(s, p, t, angle)
        return -ret

    def update(self, old_x, solve_scores, puzzle_scores):
        result = minimize(self.function_to_minimize, old_x, args=(self, solve_scores, puzzle_scores), method='Nelder-Mead')
        print(result)
        return result.x


if __name__ == '__main__':
    m = MLE(1259.77, 584.3712)
    N = 10
    t, angle = m.update((500, 100), [100 for i in range(N)], [600 for i in range(N)])
