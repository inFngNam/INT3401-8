# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random
import util

from game import Agent

SAFE_DISTANCE_TO_GHOST = 2
INF = float("INF")


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(
            gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(
            len(scores)) if scores[index] == bestScore]
        # Pick randomly among the best
        chosenIndex = random.choice(bestIndices)

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [
            ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        scaredTime = min(newScaredTimes)

        nearestGhost = min(
            [manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates])

        if nearestGhost:
            ghostScore = 10 / nearestGhost
        else:
            ghostScore = 500

        if scaredTime > SAFE_DISTANCE_TO_GHOST:
            ghostScore = 0

        nearestFood = 0
        foodList = newFood.asList()
        if foodList:
            nearestFood = min([manhattanDistance(newPos, food)
                               for food in foodList])

        numberOfFoods = len(foodList)

        score = - nearestFood - ghostScore - 50 * numberOfFoods

        return score + currentGameState.getScore()


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxBase(MultiAgentSearchAgent):
    def minValue(self, gameState, depth, agentCounter, **kwargs):
        result = ["", INF]
        ghostActions = gameState.getLegalActions(agentCounter)

        if not ghostActions:
            return self.evaluationFunction(gameState)

        for action in ghostActions:
            currentState = gameState.generateSuccessor(agentCounter, action)
            currentScore = self.solve(
                currentState, depth, agentCounter + 1, **kwargs)
            if isinstance(currentScore, float):
                score = currentScore
            else:
                score = currentScore[1]
            if score < result[1]:
                result = [action, score]
        return result

    def maxValue(self, gameState, depth, agentCounter, **kwargs):
        result = ["", -INF]
        actions = gameState.getLegalActions(agentCounter)

        if not actions:
            return self.evaluationFunction(gameState)
        for action in actions:
            currentState = gameState.generateSuccessor(agentCounter, action)
            currentScore = self.solve(
                currentState, depth, agentCounter + 1, **kwargs)
            if isinstance(currentScore, float):
                score = currentScore
            else:
                score = currentScore[1]
            if score > result[1] or (score == result[1] and result[0] == 'Stop'):
                result = [action, score]
        return result

    def isEndState(self, gameState, depth):
        return depth == self.depth or gameState.isWin() or gameState.isLose()

    def solve(self, gameState, depth, agentCounter, pacmanFunction, ghostFunction, **kwargs):
        if agentCounter == gameState.getNumAgents():
            depth += 1
            agentCounter = 0

        if (self.isEndState(gameState, depth)):
            return self.evaluationFunction(gameState)
        if (agentCounter == 0):
            return pacmanFunction(gameState, depth, agentCounter,
                                  pacmanFunction=pacmanFunction,
                                  ghostFunction=ghostFunction,
                                  **kwargs)
        return ghostFunction(gameState, depth, agentCounter,
                             pacmanFunction=pacmanFunction,
                             ghostFunction=ghostFunction,
                             **kwargs)


class MinimaxAgent(MinimaxBase):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        actions = self.solve(gameState, 0, 0,
                             pacmanFunction=self.maxValue,
                             ghostFunction=self.minValue)
        return actions[0]


class AlphaBetaAgent(MinimaxBase):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def minValueAb(self, gameState, depth, agentCounter, alpha, beta, **kwargs):
        result = ["", INF]
        ghostActions = gameState.getLegalActions(agentCounter)

        if not ghostActions:
            return self.evaluationFunction(gameState)

        for action in ghostActions:
            currentState = gameState.generateSuccessor(agentCounter, action)
            currentScore = self.solve(currentState, depth, agentCounter + 1,
                                      alpha=alpha, beta=beta, **kwargs)

            if isinstance(currentScore, float):
                score = currentScore
            else:
                score = currentScore[1]

            if score < result[1]:
                result = [action, score]
            if score < alpha:
                return [action, score]
            beta = min(beta, score)
        return result

    def maxValueAb(self, gameState, depth, agentCounter, alpha, beta, **kwargs):
        result = ["", -INF]
        actions = gameState.getLegalActions(agentCounter)

        if not actions:
            return self.evaluationFunction(gameState)

        for action in actions:
            currentState = gameState.generateSuccessor(agentCounter, action)
            currentScore = self.solve(currentState, depth, agentCounter + 1,
                                      alpha=alpha, beta=beta, **kwargs)

            if isinstance(currentScore, float):
                score = currentScore
            else:
                score = currentScore[1]

            if score > result[1]:
                result = [action, score]
            if score > beta:
                return [action, score]
            alpha = max(alpha, score)
        return result

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        actions = self.solve(gameState, 0, 0, alpha=-INF, beta=INF,
                             pacmanFunction=self.maxValueAb,
                             ghostFunction=self.minValueAb)
        return actions[0]


class ExpectimaxAgent(MinimaxBase):
    """
      Your expectimax agent (question 4)
    """

    def expectiValue(self, gameState, depth, agentCounter, **kwargs):
        ghostActions = gameState.getLegalActions(agentCounter)

        if not ghostActions:
            return self.evaluationFunction(gameState)

        result = ['', 0]
        numberOfActions = len(ghostActions)
        probabilities = 1.0 / numberOfActions

        for action in ghostActions:
            currentState = gameState.generateSuccessor(agentCounter, action)
            currentScore = self.solve(
                currentState, depth, agentCounter + 1, **kwargs)
            if isinstance(currentScore, float):
                score = currentScore
            else:
                score = currentScore[1]
            result[1] += probabilities * score
        result[0] = ghostActions[random.randint(0, numberOfActions - 1)]
        return result

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        actions = self.solve(gameState, 0, 0,
                             pacmanFunction=self.maxValue,
                             ghostFunction=self.expectiValue)
        return actions[0]


dxs = (0, 0, 1, -1)
dys = (-1, 1, 0, 0)


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).
      DESCRIPTION: <write something here so we know what you did>
    """
    dis = bfs((currentGameState))
    foods = currentGameState.getFood().asList()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    infinityScore = 10000000000
    numberOfFoods = len(foods)
    if not numberOfFoods:
        return infinityScore * 1.0
    nearestFood = min(dis[food] for food in foods)
    nearestGhost = infinityScore
    nearestScaredGhost = infinityScore
    for (ghost, time) in zip(ghostStates, scaredTimes):
        ghost_position = (
            int(ghost.getPosition()[0]), int(ghost.getPosition()[1]))
        distanceToGhost = dis[ghost_position]
        if time > 0:
            nearestScaredGhost = min(distanceToGhost, nearestScaredGhost)
        nearestGhost = min(distanceToGhost, nearestGhost)
    if nearestScaredGhost == infinityScore:
        nearestScaredGhost = 0
    if nearestScaredGhost:
        score = -nearestScaredGhost
    elif nearestGhost < SAFE_DISTANCE_TO_GHOST:
        score = -infinityScore
    else:
        score = - numberOfFoods * 100 - nearestFood * 50
    return score + currentGameState.getScore() * 1000


def out_of_bound(u, v, w, h):
    return not (0 <= u and u < w and 0 <= v and v < h)


def bfs(gameState):
    queue = util.Queue()
    pacmanPosition = gameState.getPacmanPosition()
    dis = {}
    dis[pacmanPosition] = 0
    queue.push(pacmanPosition)

    w = gameState.data.layout.width
    h = gameState.data.layout.height

    walls = gameState.getWalls().asList()

    while not queue.isEmpty():
        curVertex = queue.pop()
        u, v = curVertex
        for dx, dy in zip(dxs, dys):
            x = u + dx
            y = v + dy
            if out_of_bound(x, y, w, h):
                continue
            if (x, y) in walls or (x, y) in dis:
                continue
            dis[(x, y)] = dis[(u, v)] + 1
            queue.push((x, y))

    return dis


# Abbreviation
better = betterEvaluationFunction
