from math import e, pi, log
from scipy.optimize import minimize
from scipy.stats import norm

# maximum likelihood estimator
class MLE:
    def __init__(self, max_score, norm_spread, angle):
        self.norm_spread = norm_spread
        self.max_score = max_score
        self.angle = angle

    def expected_s(self, p, t):
        return self.max_score/(1 + e**((t-p)/self.angle)) 

    def expected_p(self, s, t):
        return t - self.angle * log(self.max_score/s - 1)

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
        return result.x[0]


if __name__ == '__main__':
    angle = 300
    ideal_score = 90
    mle = MLE(209, 94, angle)
    # starting puzzle
    starting_puzzle_diff = mle.expected_p(ideal_score, ideal_score)
    print(starting_puzzle_diff)
    # solve it in 15 moves
    new_skill = mle.get_new_true_skill(ideal_score, [starting_puzzle_diff/3], [starting_puzzle_diff])
    print(new_skill)
