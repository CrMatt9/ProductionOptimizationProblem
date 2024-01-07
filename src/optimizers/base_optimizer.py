from abc import abstractmethod
from os import getenv

from pandas import Series, DataFrame
from pyomo.core import ConcreteModel
from pyomo.opt import TerminationCondition, SolverFactory


class BaseOptimizer(ConcreteModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = None
        self.objective = None

        self.solver_path = getenv("SOLVER_PATH")
        self.solver_name = getenv("SOLVER_NAME")

    @abstractmethod
    def objective(self):
        raise NotImplementedError("Objective is not initialized")

    @abstractmethod
    def generate_results(self):
        raise NotImplementedError("Solver Path is not defined")

    @staticmethod
    def check_feasibility(results):
        """
        Checks whether the results from the optimization yielded a feasible solution or not

        :param results: results from optimization
        """
        if results.solver.termination_condition == TerminationCondition.infeasible:
            raise SystemError("Infeasible problem!")

    def solve(self):
        """
        Resolution of the LP problem with the specified solver
        :return: Results of the problem
        """
        solver = SolverFactory(self.solver_name, executable=self.solver_path)
        results = solver.solve(self, tee=False)

        self.check_feasibility(results)
        results = self.generate_results()
        return results

    @staticmethod
    def get_variable_results_on_dataframe_format(
        model_variable,
        col_headers,
    ):
        """
        Transforms a pyomo variable data to DataFrame format
        :param model_variable: Pyomo variable
        :param col_headers: Headers to use on created DataFrame
        :return: pd.DataFrame with variable info
        """
        variable_result = Series(
            model_variable.extract_values(),
            index=model_variable.extract_values().keys(),
        )
        variable_result = DataFrame(variable_result)
        variable_result = variable_result.reset_index(drop=False)
        variable_result.columns = col_headers[model_variable.id]

        return variable_result
