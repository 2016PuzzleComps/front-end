from math import e, pi, log
from scipy.optimize import minimize
from scipy.stats import norm
import sys

# maximum likelihood estimator
class MLE:
    def __init__(self, max_score, norm_spread):
        self.norm_spread = norm_spread
        self.max_score = max_score
        self.max_angle = 1000

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
        if angle > mle.max_angle:
            return sys.maxsize
        ret = 1.0
        for s, p in zip(ss, ps):
            ret *= mle.conditional_pdf(s, p, t, angle)
        # print(x[0], end="   ")
        # print(x[1], end="   ")
        # print(-ret)
        return -ret

    def update(self, old_x, solve_scores, puzzle_scores):
        result = minimize(self.function_to_minimize, old_x, args=(self, solve_scores, puzzle_scores), method='Nelder-Mead')
        return result.x


if __name__ == '__main__':
    m = MLE(1259.77, 584.3712)
    # this blows up
    print(m.update((550, 68), [500, 600], [100, 105]))
    # but these don't
    print(m.update((550, 67), [500, 600], [100, 105])) # 68 --> 67
    print(m.update((550, 500), [500, 600], [100, 100])) # 105 --> 100
