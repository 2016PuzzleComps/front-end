from math import e, pi, log
from scipy.optimize import minimize
from scipy.stats import norm

# maximum likelihood estimator
class MLE:
    def __init__(self, model):
        self.norm_spread = model.norm_spread
        self.max_score = model.get_solve_score(model.max_wwl)
        self.min_score = model.get_solve_score(model.min_wwl)
        self.ideal_score = model.ideal_score
        self.angle = (self.ideal_score - self.min_score)/(log(self.max_score/model.min_expected_score - 1) - log(self.max_score / self.ideal_score - 1))
        self.ideal_true_skill = self.ideal_score + self.angle * log(self.max_score/self.ideal_score - 1)

    def expected_solve_score(self, p, t):
        return self.max_score/(1 + e**((t-p)/self.angle)) 

    def recommended_puzzle_score(self, t):
        return t - self.angle * log(self.max_score/self.ideal_score - 1)

    def _conditional_pdf(self, s, p, t):
        loc = self.expected_solve_score(p, t)
        return norm.pdf(s, self.norm_spread, loc)

    @staticmethod
    def _function_to_minimize(t, mle, ss, ps):
        ret = 1.0
        for s, p in zip(ss, ps):
            ret *= mle._conditional_pdf(s, p, t)
        return -ret

    def get_new_true_skill(self, old_t, solve_scores, puzzle_scores):
        result = minimize(self._function_to_minimize, old_t, args=(self, solve_scores, puzzle_scores), method='Nelder-Mead')
        return result.x[0]


if __name__ == '__main__':
    import model
    mle = MLE(model)
    print("ideal score: " + str(mle.ideal_score))
    true_skill = mle.ideal_true_skill
    print("initial true skill: " + str(true_skill))
    recommended_puzzle_score = mle.recommended_puzzle_score(true_skill)
    print("recommended puzzle score: " + str(recommended_puzzle_score))
    expected_solve_score = mle.expected_solve_score(recommended_puzzle_score, true_skill)
    print("expected solve score: " + str(expected_solve_score))
    # solve it in 15 moves
    new_skill = mle.get_new_true_skill(true_skill, [expected_solve_score], [recommended_puzzle_score])
    print("new true skill after solve_score is as expected: " + str(new_skill))
