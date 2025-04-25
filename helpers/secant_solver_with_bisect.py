class Solver:
    def __init__(self, f, args, x0, dx, target, tol=1e-5, max_iter=100, bisect_min_max = [0, 1], f_increases_with_x = True):
        self.f = f
        self.args = args
        self.x0 = x0
        self.dx = dx
        self.tol = tol
        self.max_iter = max_iter
        self.bisect_min_max = bisect_min_max
        self.f_increases_with_x = f_increases_with_x
        self.target = target
        self.answer = None
    
    def solve(self):
        solved = False
        result = self.solve_secant()
        if result is None:
            result = self.solve_bisect()
            solved = result is not None
        self.answer = result
        return solved
        

    def solve_secant(self):
        x0 = self.x0
        x1 = self.x0 + self.dx
        for i in range(self.max_iter):
            f0 = self.f(x0, args=self.args) - self.target
            f1 = self.f(x1, args=self.args) - self.target

            if (f1 - f0) == 0:  # Avoid division by zero
                return None

            # Secant step
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)

            if abs(x2 - x1) < self.tol:
                return x2

            # Update points for next iteration
            x0, x1 = x1, x2

        return None
    
    def solve_bisect(self):
        x0 = self.bisect_min_max[0]
        x1 = self.bisect_min_max[1]

        for i in range(self.max_iter):
            x2 = (x0 + x1) / 2.0
            f2 = self.f(x2, args=self.args)

            if abs(f2) < self.tol:
                return x2

            if self.f_increases_with_x:
                if self.f(x2, args=self.args) < self.target:
                    x0 = x2
                else:
                    x1 = x2
            if not self.f_increases_with_x:
                if self.f(x2, args=self.args) > self.target:
                    x1 = x2
                else:
                    x0 = x2

        return None