from abc import abstractmethod

from pyomo.opt import TerminationCondition


class BaseOptimizer:
    @abstractmethod
    def objective(self):
        raise NotImplementedError("Objective is not initialized")

    @abstractmethod
    def solver_name(self):
        raise NotImplementedError("Solver Name is not defined")

    @abstractmethod
    def solver_path(self):
        raise NotImplementedError("Solver Path is not defined")

    @staticmethod
    def check_feasibility(results):
        """
        Checks whether the results from the optimization yielded a feasible solution or not

        :param results: results from optimization
        """
        if results.solver.termination_condition == TerminationCondition.infeasible:
            raise SystemError("Infeasible problem!")
