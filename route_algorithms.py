import itertools
from itertools import combinations

INF = float("inf")


def calculate_route_distance(route, dist):
    """Total distance of a route, including the return to the warehouse."""
    total = 0
    for i in range(len(route) - 1):
        total += dist[route[i]][route[i + 1]]
    total += dist[route[-1]][route[0]]  # return trip
    return total


def nearest_neighbour(dist):
    """Greedy: always go to the nearest unvisited location."""
    n = len(dist)
    route = [0]
    visited = [False] * n
    visited[0] = True
    current = 0
    while len(route) < n:
        nxt = None
        for j in range(n):
            if not visited[j] and (nxt is None or dist[current][j] < dist[current][nxt]):
                nxt = j
        route.append(nxt)
        visited[nxt] = True
        current = nxt
    return route, calculate_route_distance(route, dist)


def brute_force(dist):
    """Try every order of the other locations, keep the minimum."""
    n = len(dist)
    best_route, best = None, INF
    for perm in itertools.permutations(range(1, n)):
        route = [0] + list(perm)
        d = calculate_route_distance(route, dist)
        if d < best:
            best, best_route = d, route
    return best_route, best


def dynamic_programming(dist):
    """Held-Karp: dp[(mask, j)] = shortest path starting at 0, visiting
    the locations in mask, and ending at j. Bit (k-1) of mask = location k."""
    n = len(dist)
    if n == 1:
        return [0], 0
    dp, parent = {}, {}
    for j in range(1, n):
        dp[(1 << (j - 1), j)] = dist[0][j]
        parent[(1 << (j - 1), j)] = 0

    for size in range(2, n):
        for subset in combinations(range(1, n), size):
            mask = sum(1 << (k - 1) for k in subset)
            for j in subset:
                prev = mask ^ (1 << (j - 1))
                best, best_k = INF, None
                for k in subset:
                    if k == j:
                        continue
                    cost = dp[(prev, k)] + dist[k][j]
                    if cost < best:
                        best, best_k = cost, k
                dp[(mask, j)] = best
                parent[(mask, j)] = best_k

    full = (1 << (n - 1)) - 1
    best, last = INF, None
    for j in range(1, n):
        cost = dp[(full, j)] + dist[j][0]
        if cost < best:
            best, last = cost, j

    # rebuild route using the parent map
    route, mask, j = [], full, last
    while j != 0:
        route.append(j)
        pj = parent[(mask, j)]
        mask ^= 1 << (j - 1)
        j = pj
    route.append(0)
    route.reverse()
    return route, best