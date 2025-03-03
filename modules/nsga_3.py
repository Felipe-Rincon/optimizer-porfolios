import numpy as np
import math
from numpy.random import seed, rand

import time

from itertools import combinations

seed(int(time.time())) 

ROOT365 = math.sqrt(365)
print("ROOT365:", ROOT365)

def generateValue(constraint):
    return constraint['min_weight'] + (rand() * (constraint['max_weight'] - constraint['min_weight']))

def normalize(values):
    sum_val = sum(values)
    return [value / sum_val for value in values]

def generateDoubleArray(constraints):
    return normalize([generateValue(constraint) for constraint in constraints])

def adjustOutlier(value, minWeight, maxWeight):
    if value < minWeight:
        return minWeight + (0.3 * rand() * (maxWeight - minWeight))
    elif value > maxWeight:
        return maxWeight - (0.3 * rand() * (maxWeight - minWeight))
    return value

def repair(solution, constraints):
    repeat = True
    while repeat:
        repeat = False
        for i in range(len(constraints['single'])):
            solution[i] = adjustOutlier(solution[i], constraints['single'][i]['min_weight'], constraints['single'][i]['max_weight'])
        solution = normalize(solution)
        for constraint in constraints['grouped']:
            sum_val = sum(solution[index] for index in constraint['indexes'])
            multiplier = -0.1 if sum_val < constraint['min_weight'] else (0.1 if sum_val > constraint['max_weight'] else 0)
            if multiplier != 0:
                for index in constraint['indexes']:
                    solution[index] *= (1.0 - (multiplier * rand()))
        solution = normalize(solution)
        for i in range(len(constraints['single'])):
            if (solution[i] < constraints['single'][i]['min_weight']) or (solution[i] > constraints['single'][i]['max_weight']):
                repeat = True
        for constraint in constraints['grouped']:
            sum_val = sum(solution[index] for index in constraint['indexes'])
            if (sum_val < constraint['min_weight']) or (sum_val > constraint['max_weight']):
                repeat = True
    return solution

def generateIndividual(constraints):
    return repair(generateDoubleArray(constraints['single']), constraints)

def generatePopulation(constraints, popsize):
    return [generateIndividual(constraints) for _ in range(popsize)]

def average(values):
    return sum(values) / len(values)

def deviation(values):
    avg = average(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))

class ExpectedReturnFunction:
    def __init__(self):
        self.name = 'Expected Return'
    
    def apply(self, solution, values):
        return sum(solution[i] * values[i]['expected_return'] for i in range(len(solution)))
    
    def compare(self, value1, value2):
        if abs(value1 - value2) < 1e-9:
            return 0
        return 1 if value1 > value2 else -1
    
class ExpectedReturnForecastFunction:
    def  __init__(self):
        self.name = 'Expected Return Forecast'
    
    def apply(self, solution, values):
        return sum(solution[i] * values[i]['expected_return_forecast'] for i in range(len(solution)))
    
    def compare(self, value1, value2):
        if abs(value1 - value2) < 1e-9:
            return 0
        return 1 if value1 > value2 else -1
        
class VolatilityFunction:
    def __init__(self):
        self.name = 'Volatility'
    
    def generateUnitValues(self, solution, values):
        units = [100]
        for i in range(len(values[0]['historical_returns'])):
            sum_val = sum(values[j]['historical_returns'][i] * solution[j] for j in range(len(solution)))
            units.append(units[i] * (1 + sum_val))
        return units
    
    def calculateReturn(self, actualval, nextval):
        return 0 if nextval == actualval else (nextval / actualval) - 1
    
    def calculateReturns(self, prices):
        return [self.calculateReturn(prices[i], prices[i + 1]) for i in range(len(prices) - 1)]
    
    def apply(self, solution, values):
        returns = self.calculateReturns(self.generateUnitValues(solution, values))
        return deviation(returns) * ROOT365
    
    def compare(self, value1, value2):
        if abs(value1 - value2) < 1e-9:
            return 0
        return 1 if value1 < value2 else -1
    
class DownsideRiskFunction:
    def __init__(self):
        self.name = 'Downside Risk'
        
    def generateUnitValues(self, solution, values):
        units = [100]
        for i in range(len(values[0]['historical_returns'])):
            sum_val = sum(values[j]['historical_returns'][i] * solution[j] for j in range(len(solution)))
            units.append(units[i] * (1 + sum_val))
        return units
    
    def calculateReturn(self, actualval, nextval):
        return 0 if nextval == actualval else (nextval / actualval) - 1
    
    def calculateReturns(self, prices):
        return [self.calculateReturn(prices[i], prices[i + 1]) for i in range(len(prices) - 1)]
    
    def removePositive(self, returns):
        return [ret for ret in returns if ret < 0]
    
    def apply(self, solution, values):
        returns = self.removePositive(self.calculateReturns(self.generateUnitValues(solution, values)))
        return deviation(returns) * ROOT365
    
    def compare(self, value1, value2):
        if abs(value1 - value2) < 1e-9:
            return 0
        return 1 if value1 < value2 else -1


class MaxDrawdownFunction:
    def __init__(self):
        self.name = 'Maximum Drawdown'
    
    def generateUnitValues(self, solution, values):
        units = [100]
        for i in range(len(values[0]['historical_returns'])):
            sum_val = sum(values[j]['historical_returns'][i] * solution[j] for j in range(len(solution)))
            units.append(units[i] * (1 + sum_val))
        return units
    
    def calculateDrawdown(self, prices):
        peak = prices[0]
        max_drawdown = 0
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        return max_drawdown
    
    def apply(self, solution, values):
        unit_values = self.generateUnitValues(solution, values)
        return self.calculateDrawdown(unit_values)
    
    def compare(self, value1, value2):
        if abs(value1 - value2) < 1e-9:
            return 0
        return 1 if value1 < value2 else -1

class DurationFunction:
    def __init__(self):
        self.name = 'Duration'
    
    def apply(self, solution, values):
        return sum(solution[i] * values[i]['duration'] for i in range(len(solution)))
    

def functions_generator(functions_entry):

    functions = [eval(functions) for functions in functions_entry]

    return functions

#functions = [ExpectedReturnFunction(), VolatilityFunction(), MaxDrawdownFunction()]

def dominate(performance1, performance2, functions):
    dominance = False
    for i in range(len(functions)):
        cmp = functions[i].compare(performance1[i], performance2[i])
        if cmp < 0:
            return False
        elif cmp > 0:
            dominance = True
    return dominance

def evaluate(assetValues, population, functions):
    return [[func.apply(individual, assetValues) for func in functions] for individual in population]

def evaluate_portfolios(assetValues, population, functions_entry):
    functions = functions_generator(functions_entry) + [DurationFunction()]
    return [[func.apply(individual, assetValues) for func in functions] for individual in population]

def nonDominatedSort(population, performances, functions):
    fronts = []
    dominatedCount = [0] * len(population)
    dominates = [[] for _ in range(len(population))]
    
    for i in range(len(population)):
        for j in range(len(population)):
            if i == j:
                continue
            if dominate(performances[i], performances[j], functions):
                dominates[i].append(j)
            elif dominate(performances[j], performances[i], functions):
                dominatedCount[i] += 1
        if dominatedCount[i] == 0:
            if len(fronts) == 0:
                fronts.append([])
            fronts[0].append(i)
    
    if len(fronts) == 0:
        fronts.append(list(range(len(population))))
    
    i = 0
    while i < len(fronts) and len(fronts[i]) > 0:
        nextFront = []
        for idx in fronts[i]:
            for dominatedIdx in dominates[idx]:
                dominatedCount[dominatedIdx] -= 1
                if dominatedCount[dominatedIdx] == 0:
                    nextFront.append(dominatedIdx)
        if len(nextFront) > 0:
            fronts.append(nextFront)
        i += 1
    
    return fronts

def generateReferencePoints(num_objs, num_divisions):
    ref_points = []
    if num_objs == 1:
        return [[1.0]]
    for comb in combinations(range(num_objs + num_divisions - 1), num_objs - 1):
        ref_point = [0] * num_objs
        prev = -1
        for i in range(num_objs - 1):
            ref_point[i] = (comb[i] - prev - 1) / num_divisions
            prev = comb[i]
        ref_point[-1] = (num_objs + num_divisions - 1 - comb[-1] - 1) / num_divisions
        ref_points.append(ref_point)
    return ref_points

def associateToReferencePoints(population, performances, ref_points, functions):
    num_objs = len(functions)
    niche_counts = [0] * len(ref_points)
    distances = [[] for _ in range(len(ref_points))]
    for i in range(len(population)):
        min_dist = float('inf')
        closest_ref = 0
        for j in range(len(ref_points)):
            dist = math.sqrt(sum((performances[i][k] - ref_points[j][k]) ** 2 for k in range(num_objs)))
            if dist < min_dist:
                min_dist = dist
                closest_ref = j
        distances[closest_ref].append((i, min_dist))
        niche_counts[closest_ref] += 1
    return distances, niche_counts

def nichingSelection(population, performances, ref_points, niche_counts, distances, popsize):
    selected = []
    remaining = popsize
    while remaining > 0:
        min_count = min(niche_counts)
        for i in range(len(ref_points)):
            if niche_counts[i] == min_count and len(distances[i]) > 0:
                distances[i].sort(key=lambda x: x[1])
                selected.append(population[distances[i][0][0]])
                distances[i].pop(0)
                niche_counts[i] += 1
                remaining -= 1
                if remaining == 0:
                    break
    return selected

def mutate(parent, constraints):
    child = []
    cut = math.floor(rand() * len(parent))
    for i in range(len(parent)):
        if cut == i:
            if rand() < 0.5:
                child.append(generateValue(constraints['single'][i]))
            else:
                child.append(parent[i] * 2 * rand())
        else:
            child.append(parent[i])
    return [repair(child, constraints)]

def arithmeticCrossover(parent1, parent2, constraints):
    alpha = rand()
    child1 = [(alpha * parent1[i]) + ((1 - alpha) * parent2[i]) for i in range(len(parent1))]
    child2 = [((1 - alpha) * parent1[i]) + (alpha * parent2[i]) for i in range(len(parent1))]
    return [repair(child1, constraints), repair(child2, constraints)]

def main(assetValues, constraints, popsize, iters, functions_entry):
    functions = functions_generator(functions_entry)
    num_objs = len(functions)
    ref_points = generateReferencePoints(num_objs, 4)
    population = generatePopulation(constraints, popsize)
    for i in range(iters):
        print(f"Iteration {i}: Population size = {len(population)}")
        print('f', functions)
        performances = evaluate(assetValues, population, functions)
        fronts = nonDominatedSort(population, performances, functions)
        next_population = []
        for front in fronts:
            if len(next_population) + len(front) <= popsize:
                next_population.extend([population[idx] for idx in front])
            else:
                distances, niche_counts = associateToReferencePoints(population, performances, ref_points, functions)
                next_population.extend(nichingSelection(population, performances, ref_points, niche_counts, distances, popsize - len(next_population)))
                break
        offspring = []
        for individual in next_population:
            if rand() < 0.5:
                offspring.extend(mutate(individual, constraints))
            else:
                piv = math.floor(rand() * len(next_population))
                offspring.extend(arithmeticCrossover(individual, next_population[piv], constraints))
        population = next_population + offspring
        print(len(population))
    return population