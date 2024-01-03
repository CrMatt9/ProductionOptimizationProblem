# ProductionOptimizationProblem

In a factory dedicated to the manufacturing of consumer goods are produced the products A and B with
certain equipment’s E1 and E2. To produce the products A and B are necessary the raw materials M1, M2
and M3. Each equipment can produce a product according to a compatible formula. For instance, formula
FA is compatible with equipment E1 and produce 1 unit of product A using 0.3 units of raw material M1,
0.2 units of M2 and 0.5 units of M3. Each equipment has a maximum production capacity (can produce
between 0 and the maximum value, in steps of integers of 10 units) and a maximum continuous operation
time (after that it must be cleaned for 1 hour) At the beginning of the planning, exists in inventory an initial
stock of both products and materials. If the stock of raw materials is not enough to produce the expected
quantity of products, it can be purchased more materials. This purchase can be done in any time step
during the planning horizon. Assume that the supply of the materials purchased is delivered 1 hour after
the purchased. The objective is to find the optimal production schedule that satisfy the demand of final
products in the planning horizon, minimizing the total cost (operational cost and purchase cost). At the
end of the planning horizon the stock of both products and materials must be equal or greater that the
safety stock. The resolution of the schedule must be hours. The equipment can operate between 8am to
20pm. Consider that the demand of a given product in each period/day T is satisfied from 8 am to 9 am in
the next period/day (T+1). Consider that the equipment’s are cleaned and ready to produce at the
beginning of the planning.