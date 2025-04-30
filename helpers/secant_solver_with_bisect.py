class Solver:
    def __init__(self, f, args, x0, dx, target, easy_tol=1e-5, strict_tol = 1e-10, specified_tol = None, max_iter=100, bisect_min_max = [0, 1], f_increases_with_x = True):
        self.f = f
        self.args = args
        self.x0 = x0
        self.dx = dx
        self.tols = {
            "easy": easy_tol,
            "strict": strict_tol
        }
        if specified_tol is not None:
            self.tols = {
                "easy": specified_tol,
                "strict": specified_tol
            }
        self.max_iter = max_iter
        self.bisect_min_max = bisect_min_max
        self.f_increases_with_x = f_increases_with_x
        self.target = target
        self.answer = None
        self.solved_method = None
        self.iters = {
            "secant": 0,
            "bisect": 0
        }
        self.solver_data = {
            "secant": {
                "x0": x0,
                "x1": x0 + dx,
                "f0": None,
                "f1": None,
                "x2": None
            },
            "bisect": {
                "x0": bisect_min_max[0],
                "x1": bisect_min_max[1],
                "x2": None,
                "f2": None
            }
        }
    
    def solve(self):
        solved = False
        result = self.solve_secant()
        if result is None:
            result = self.solve_bisect()
        solved = result is not None
        self.answer = result
        return solved
        

    def solve_secant(self):
        tol = self.tols["strict"]
        x0 = self.x0
        x1 = self.x0 + self.dx
        for i in range(self.max_iter):
            self.iters["secant"] += 1
            f0 = self.f(x0, args=self.args) - self.target
            f1 = self.f(x1, args=self.args) - self.target

            if (f1 - f0) == 0:  # Avoid division by zero
                return None

            # Secant step
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)

            self.solver_data["secant"]["x0"] = x0
            self.solver_data["secant"]["x1"] = x1
            self.solver_data["secant"]["x2"] = x2
            self.solver_data["secant"]["f0"] = f0
            self.solver_data["secant"]["f1"] = f1

            

            if abs(x2 - x1) < tol:
                self.solved_method = "secant"
                return x2
            

            # Update points for next iteration
            x0, x1 = x1, x2

        return None
    
    def solve_bisect(self):
        tol = self.tols["strict"]
        x0 = self.bisect_min_max[0]
        x1 = self.bisect_min_max[1]

        for i in range(self.max_iter):
            self.iters["bisect"] += 1
            x2 = (x0 + x1) / 2.0
            f2 = self.f(x2, args=self.args)

            if abs(f2 - self.target) < tol:
                self.solved_method = "bisect"
                return x2
            
            self.solver_data["bisect"]["x0"] = x0
            self.solver_data["bisect"]["x1"] = x1
            self.solver_data["bisect"]["x2"] = x2
            self.solver_data["bisect"]["f2"] = f2

            if self.f_increases_with_x:
                if f2 < self.target:
                    x0 = x2
                else:
                    x1 = x2
            if not self.f_increases_with_x:
                if f2 > self.target:
                    x0 = x2
                else:
                    x1 = x2

        return None