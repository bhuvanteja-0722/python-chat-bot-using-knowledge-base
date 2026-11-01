"""A small command-line Python question-answering chatbot."""

from __future__ import annotations

import re
from difflib import get_close_matches
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeEntry:
    question: str
    answer: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...] = ()


KNOWLEDGE_BASE = (
    KnowledgeEntry(
        "What is Python?",
        "Python is a high-level, general-purpose programming language known for readable syntax and a large standard library.",
        ("language",), ("what is python", "about python"),
    ),
    KnowledgeEntry(
        "How do I define a function?",
        "Use `def`, followed by the function name, parentheses, and a colon. Indent the function body:\n\n```python\ndef greet(name):\n    return f\"Hello, {name}!\"\n```",
        ("function", "define", "def", "parameter", "return"), ("create a function", "write a function"),
    ),
    KnowledgeEntry(
        "What are Python lists?",
        "A list is an ordered, mutable collection. Create one with square brackets, such as `numbers = [1, 2, 3]`. Use `append()` to add an item and indexing like `numbers[0]` to access one.",
        ("list", "lists", "append", "mutable", "collection"), ("python array", "add to a list"),
    ),
    KnowledgeEntry(
        "What is a hash table or map?",
        "A hash table (also called a hash map) stores key-value pairs and uses a hash function to find values quickly on average. Python's built-in `dict` is a hash table: `ages = {\"Ada\": 36}`. Keys must be hashable; collisions are handled internally. A plain `map` can also mean Python's `map(function, items)`, so use the surrounding context to distinguish them.",
        ("hash", "table", "map", "mapping", "key", "value", "dict"), ("hash table", "hash map", "hash table map", "map data structure"),
    ),
    KnowledgeEntry(
        "How do I use a queue in Python?",
        "A queue is a first-in, first-out (FIFO) structure: add items at the back and remove them from the front. For an efficient queue, use `collections.deque` rather than removing index 0 from a list:\n\n```python\nfrom collections import deque\nqueue = deque()\nqueue.append(\"first\")  # enqueue\nitem = queue.popleft()   # dequeue\n```",
        ("queue", "fifo", "enqueue", "dequeue", "first-in-first-out"), ("fifo queue", "python queue", "queue data structure"),
    ),
    KnowledgeEntry(
        "What is a deque?",
        "A deque (double-ended queue) supports efficient appends and removals at both ends. Python's `collections.deque` provides `append`, `appendleft`, `pop`, and `popleft`. Use it for queues, sliding windows, or worklists; use a list for fast random indexing.",
        ("deque", "double", "ended", "queue", "appendleft", "popleft"), ("double ended queue", "double-ended queue"),
    ),
    KnowledgeEntry(
        "What is an array in Python?",
        "An array stores an indexed sequence of items. Python lists are dynamic arrays and are the usual general-purpose choice. The standard-library `array.array` stores compact, same-type numeric values; NumPy arrays are popular for numerical computing but require installing NumPy.",
        ("array", "arrays", "indexed", "contiguous", "numpy"), ("python array", "array data structure", "dynamic array"),
    ),
    KnowledgeEntry(
        "How do I make a circular queue?",
        "A circular queue reuses a fixed-size buffer as its indices wrap around. For a simple bounded queue, `deque(maxlen=capacity)` is convenient, but it silently discards the oldest item when full. If a full queue should reject new items instead, check the capacity before appending:\n\n```python\nfrom collections import deque\ncapacity = 3\nqueue = deque()\n\ndef enqueue(item):\n    if len(queue) == capacity:\n        raise OverflowError(\"queue is full\")\n    queue.append(item)\n```\nUse `popleft()` to dequeue. For a thread-safe producer/consumer queue, use `queue.Queue`.",
        ("circular", "queue", "fifo", "ring", "buffer", "wrap", "deque", "capacity"), ("circular queue", "circular buffer", "ring buffer"),
    ),
    KnowledgeEntry(
        "How do I use a thread-safe queue?",
        "Use `queue.Queue` to safely pass items between threads. Call `put(item)` to add and `get()` to remove the next item; `get()` blocks while the queue is empty. Call `task_done()` after processing each item when coordinating with `join()`.",
        ("queue", "thread", "thread-safe", "producer", "consumer", "put", "get"), ("queue module", "thread safe queue", "producer consumer queue"),
    ),
    KnowledgeEntry(
        "How do I implement a stack?",
        "A stack is last-in, first-out (LIFO). A Python list works well: use `append(item)` to push and `pop()` to remove the most recently added item. Use `deque` if you need fast operations at both ends.",
        ("stack", "lifo", "push", "pop", "last-in-first-out"), ("stack data structure", "python stack"),
    ),
    KnowledgeEntry(
        "How can a stack evaluate a postfix expression?",
        "Scan tokens from left to right. Push numbers; when an operator appears, pop its operands, apply the operator, and push the result. One final stack value is the answer. For subtraction and division, preserve operand order: the first popped value is the right operand.",
        ("stack", "postfix", "expression", "evaluate", "operator", "operand"), ("postfix evaluation", "evaluate postfix expression", "reverse polish notation"),
    ),
    KnowledgeEntry(
        "How do I make a priority queue?",
        "Use the standard-library `heapq` module for a min-priority queue. Store `(priority, item)` pairs; the smallest priority is removed first:\n\n```python\nimport heapq\ntasks = []\nheapq.heappush(tasks, (2, \"later\"))\nheapq.heappush(tasks, (1, \"sooner\"))\npriority, task = heapq.heappop(tasks)\n```",
        ("priority", "queue", "heapq", "priorityqueue"), ("priority queue", "min heap"),
    ),
    KnowledgeEntry(
        "What is a linked list?",
        "A linked list is a chain of nodes where each node points to the next. Python does not have a built-in linked-list type; lists and `collections.deque` are usually faster and simpler for everyday work. Linked lists are mainly useful when learning data structures or when node-based operations are required.",
        ("linked", "list", "node", "pointer", "next"), ("linked list", "singly linked list", "doubly linked list"),
    ),
    KnowledgeEntry(
        "How do I approach a data-structures problem?",
        "Use a repeatable workflow:\n1. Restate the task and clarify input, output, limits, and edge cases.\n2. Work through a small example by hand.\n3. Describe a simple correct solution first.\n4. Choose a data structure or algorithm that reduces the expensive work.\n5. State why it is correct, then estimate time and extra space.\n6. Implement in small steps and check empty, smallest, typical, and boundary inputs.\n7. Compare the result with the original examples and revise if needed.",
        ("approach", "problem", "solve", "workflow", "strategy", "algorithm", "design"), ("problem solving", "solve a coding problem", "approach an algorithm problem", "solve a data structures problem"),
    ),
    KnowledgeEntry(
        "How do I choose a data structure?",
        "Start from the operations the program needs: indexed access suggests a list; fast key lookup suggests a dict; unique membership suggests a set; FIFO work suggests a deque; LIFO work suggests a list; minimum-priority removal suggests `heapq`. Compare operation costs, memory, ordering, and update patterns before choosing.",
        ("choose", "data", "structure", "operations", "lookup", "access", "tradeoff"), ("choose a data structure", "which data structure should i use"),
    ),
    KnowledgeEntry(
        "What is an abstract data type?",
        "An abstract data type (ADT) describes what operations a collection supports and what they mean, without requiring one particular internal representation. A stack ADT, for example, provides push and pop; it can be implemented with a Python list or a linked structure.",
        ("abstract", "data", "type", "adt", "interface", "operation"), ("abstract data type", "adt"),
    ),
    KnowledgeEntry(
        "How do I reason about algorithm correctness?",
        "State what must be true before and after each step. For a loop, use an invariant: show it is true before the first iteration, stays true after every iteration, and implies the result when the loop ends. Then check termination and edge cases.",
        ("correctness", "proof", "invariant", "loop", "termination", "reasoning"), ("prove an algorithm", "loop invariant", "algorithm correctness"),
    ),
    KnowledgeEntry(
        "What is amortized analysis?",
        "Amortized analysis bounds the average cost per operation over any sequence of operations, even when an occasional operation is expensive. A dynamic array append is usually O(1) amortized: most appends are cheap, while a resize copies items only occasionally.",
        ("amortized", "analysis", "dynamic", "array", "append", "resize", "cost"), ("amortized analysis", "amortized complexity"),
    ),
    KnowledgeEntry(
        "How do I check whether two strings are anagrams?",
        "Normalize the strings according to the problem's rules, then compare character counts. This is O(n) time and O(k) extra space for k distinct characters:\n\n```python\nfrom collections import Counter\n\ndef are_anagrams(first, second):\n    return Counter(first) == Counter(second)\n```\nIf spaces or letter case should be ignored, normalize them before counting.",
        ("anagram", "anagrams", "character", "frequency", "count", "string"), ("anagram detection", "check anagrams", "anagram problem"),
    ),
    KnowledgeEntry(
        "How do I check balanced parentheses?",
        "Scan left to right with a stack. Push each opening bracket; for a closing bracket, check and remove the matching opener. The string is balanced only if every close matched and the stack ends empty. This takes O(n) time and O(n) worst-case space.",
        ("balanced", "parentheses", "bracket", "brackets", "stack", "symbol"), ("balanced parentheses", "matching brackets", "balanced symbols"),
    ),
    KnowledgeEntry(
        "How do I find the shortest word ladder?",
        "Model each word as a graph vertex and connect words that differ by one letter. Breadth-first search finds the shortest ladder when each change has equal cost. Track visited words to avoid revisiting nodes; precomputed wildcard buckets can make neighbor lookup faster.",
        ("word", "ladder", "shortest", "bfs", "breadth", "graph", "path"), ("word ladder", "word transformation problem"),
    ),
    KnowledgeEntry(
        "How do I traverse a tree?",
        "Depth-first traversals include preorder (node, left, right), inorder (left, node, right), and postorder (left, right, node). Breadth-first traversal visits level by level with a queue. Each traversal visits n nodes in O(n) time.",
        ("traverse", "traversal", "tree", "preorder", "inorder", "postorder", "breadth"), ("tree traversal", "traverse a tree"),
    ),
    KnowledgeEntry(
        "What is a tree data structure?",
        "A tree is a hierarchical structure of nodes connected by edges, often with one root. Python has no general-purpose built-in tree container; represent nodes with a small class or dataclass and store child nodes in a list or dictionary.",
        ("tree", "node", "root", "child", "parent", "hierarchy"), ("tree data structure", "binary tree"),
    ),
    KnowledgeEntry(
        "What is a binary search tree?",
        "A binary search tree (BST) is a binary tree ordered so values in the left subtree are smaller and values in the right subtree are larger (the exact duplicate rule depends on the implementation). Search, insert, and delete take O(log n) on a balanced tree but can degrade to O(n) if it becomes skewed.",
        ("binary", "search", "tree", "bst", "ordered", "balanced"), ("binary search tree", "bst"),
    ),
    KnowledgeEntry(
        "What is a heap?",
        "A heap is a tree-shaped priority structure that keeps the smallest (min-heap) or largest (max-heap) item at the root. Python's `heapq` provides a min-heap using a list: `heappush()` inserts and `heappop()` removes the smallest item, each in O(log n).",
        ("heap", "heaps", "heapq", "minheap", "maxheap", "priority"), ("heap data structure", "binary heap"),
    ),
    KnowledgeEntry(
        "What are advanced data structures?",
        "Advanced structures solve specialized problems: tries index prefixes, segment/Fenwick trees answer range queries, union-find tracks connected components, and Bloom filters test set membership approximately. Choose one only when its operations fit the workload; Python's `dict`, `set`, `list`, and `deque` are enough for many applications.",
        ("advanced", "structure", "structures", "data", "specialized"), ("advanced data structures", "advanced structures"),
    ),
    KnowledgeEntry(
        "What is a graph data structure?",
        "A graph contains vertices (nodes) connected by edges. A common Python representation is an adjacency dictionary, such as `graph = {\"A\": [\"B\", \"C\"]}`. Use a set for neighbors when fast membership checks matter.",
        ("graph", "vertex", "vertices", "edge", "adjacency", "node"), ("graph data structure", "adjacency list"),
    ),
    KnowledgeEntry(
        "What is the difference between an adjacency list and matrix?",
        "An adjacency list stores each vertex's neighbors and uses O(V + E) space, so it suits sparse graphs. An adjacency matrix uses O(V²) space but checks whether an edge exists in O(1), which can suit dense graphs. Choose based on graph density and the operations needed.",
        ("adjacency", "list", "matrix", "graph", "space", "edge"), ("adjacency list vs matrix", "adjacency list and matrix", "adjacency matrix vs list", "graph representation"),
    ),
    KnowledgeEntry(
        "What are BFS and DFS?",
        "Breadth-first search (BFS) explores a graph level by level, usually with a queue. Depth-first search (DFS) follows a path before backtracking, using a stack or recursion. Track visited nodes so cycles do not cause infinite traversal.",
        ("bfs", "dfs", "breadth", "depth", "search", "traversal", "graph"), ("breadth first search", "depth first search", "graph traversal"),
    ),
    KnowledgeEntry(
        "How does binary search work?",
        "Binary search finds a value in a sorted sequence by repeatedly halving the search range, taking O(log n) comparisons. The input must already be sorted. Python's `bisect` module provides insertion-point searches for sorted lists.",
        ("binary", "search", "sorted", "bisect", "logarithmic"), ("binary search", "search a sorted list"),
    ),
    KnowledgeEntry(
        "What is searching in algorithms?",
        "Searching finds an item or position. A linear scan works on any iterable and takes O(n); binary search takes O(log n) but requires sorted data. For repeated membership checks, a set or dictionary usually offers O(1) average lookup.",
        ("searching", "search", "find", "lookup", "linear", "algorithm"), ("search algorithms", "searching algorithms"),
    ),
    KnowledgeEntry(
        "How do I sort values in Python?",
        "Use `sorted(values)` to make a new sorted list or `values.sort()` to sort a list in place. Pass `key=` to choose what to compare, and `reverse=True` for descending order. Python's sort is stable.",
        ("sort", "sorting", "sorted", "order", "key", "reverse"), ("sort a list", "sorting a list"),
    ),
    KnowledgeEntry(
        "How do common sorting algorithms compare?",
        "Bubble, selection, and insertion sort are usually O(n²); insertion sort can be useful on small or nearly sorted inputs. Merge sort is O(n log n), stable, and uses extra memory. Quicksort is O(n log n) on average but O(n²) in the worst case. In real Python code, prefer the stable built-in `sorted()` unless you are studying or need a special algorithm.",
        ("sorting", "algorithm", "bubble", "selection", "insertion", "merge", "quick", "compare"), ("sorting algorithms", "compare sorting methods", "sorting methods"),
    ),
    KnowledgeEntry(
        "What is merge sort?",
        "Merge sort divides a sequence into halves, sorts each half, then merges them. It runs in O(n log n) time and is stable, with O(n) extra memory for the usual array implementation.",
        ("merge", "sort", "sorting", "divide", "conquer"), ("merge sort",),
    ),
    KnowledgeEntry(
        "What is quicksort?",
        "Quicksort partitions values around a pivot and recursively sorts the partitions. Its average time is O(n log n), but poor pivots can lead to O(n²) worst-case time. Python's built-in sort is usually the better practical choice.",
        ("quick", "sort", "quicksort", "pivot", "partition"), ("quick sort", "quicksort"),
    ),
    KnowledgeEntry(
        "What is insertion sort?",
        "Insertion sort grows a sorted prefix by inserting each next item into its proper position. It takes O(n²) time in general, but is simple and performs well on small or nearly sorted sequences.",
        ("insertion", "sort", "sorting", "nearly", "sorted"), ("insertion sort",),
    ),
    KnowledgeEntry(
        "What is sequential or linear search?",
        "Linear search checks items one by one until it finds a match or reaches the end. It works on unsorted data and takes O(n) time in the worst case. For repeated lookups, consider sorting once or using a set/dictionary.",
        ("sequential", "linear", "search", "unsorted", "lookup"), ("sequential search", "linear search"),
    ),
    KnowledgeEntry(
        "What is Big O notation?",
        "Big O notation describes how an algorithm's resource use grows as input size grows, ignoring constant factors. Common rates are O(1), O(log n), O(n), O(n log n), and O(n²). For example, binary search is O(log n), while scanning a list is O(n).",
        ("big", "o", "notation", "asymptotic", "algorithm"), ("big o notation", "big-o notation", "order of growth"),
    ),
    KnowledgeEntry(
        "What is time complexity?",
        "Time complexity describes how an algorithm's running work grows with input size. A single pass is usually O(n); two nested passes over the same input are usually O(n²); binary search is O(log n). These are growth estimates, not a promise about elapsed seconds.",
        ("time", "complexity", "runtime", "running", "algorithm", "growth"), ("time complexity", "runtime complexity"),
    ),
    KnowledgeEntry(
        "What is space complexity?",
        "Space complexity describes how extra memory use grows with input size. A loop that stores no input-sized data may use O(1) auxiliary space; copying an n-item list uses O(n). State whether you count the input itself when comparing algorithms.",
        ("space", "complexity", "memory", "auxiliary", "algorithm", "growth"), ("space complexity", "memory complexity", "auxiliary space"),
    ),
    KnowledgeEntry(
        "What are the two-pointer and sliding-window techniques?",
        "Two pointers track two positions in a sequence, often moving inward or forward to solve a problem in one pass. A sliding window keeps a range of items and updates it as the endpoints move. Both can reduce repeated work from O(n²) to O(n), but the correct approach depends on the problem and its input ordering.",
        ("two", "pointer", "pointers", "sliding", "window", "technique", "algorithm", "sequence"), ("two pointer technique", "two pointers", "sliding window", "two pointers sliding window"),
    ),
    KnowledgeEntry(
        "What is a greedy algorithm?",
        "A greedy algorithm makes the best-looking local choice at each step. It is correct only when those choices can be shown to lead to a global optimum; test the reasoning with a proof or counterexample. Greedy methods are common for interval scheduling and some coin systems.",
        ("greedy", "approach", "algorithm", "local", "optimal"), ("greedy algorithm", "greedy approach"),
    ),
    KnowledgeEntry(
        "What is dynamic programming?",
        "Dynamic programming solves a problem by reusing answers to overlapping subproblems. Define the state, recurrence, and base cases; then use memoization (top-down) or a table (bottom-up). It often trades extra memory for less repeated computation.",
        ("dynamic", "programming", "memoization", "tabulation", "subproblem", "recurrence"), ("dynamic programming", "dp", "memoization"),
    ),
    KnowledgeEntry(
        "What is backtracking?",
        "Backtracking often uses recursion to explore choices: make a choice, recurse, then undo it before trying another. Stop at a base case when a solution is complete; prune branches that cannot work. It is commonly used for permutations, combinations, and constraint puzzles, but worst-case search can be exponential.",
        ("backtracking", "backtrack", "search", "candidate", "prune"), ("backtracking algorithm", "recursion and backtracking"),
    ),
    KnowledgeEntry(
        "What is divide and conquer?",
        "Divide and conquer breaks a problem into smaller independent subproblems, solves them, then combines their results. Merge sort and binary search are examples. Analyze the recurrence to estimate its time complexity.",
        ("divide", "conquer", "subproblem", "combine", "recurrence", "algorithm"), ("divide and conquer", "divide-and-conquer"),
    ),
    KnowledgeEntry(
        "What is a trie?",
        "A trie (prefix tree) stores strings by sharing nodes for common prefixes. It supports prefix lookup in O(length of the key), independent of how many keys are stored, at the cost of extra memory. Tries are useful for autocomplete and dictionaries of words.",
        ("trie", "prefix", "autocomplete", "string", "dictionary"), ("trie data structure", "prefix tree"),
    ),
    KnowledgeEntry(
        "What are segment trees and Fenwick trees?",
        "A segment tree answers range queries and supports point or range updates, commonly in O(log n), using O(n) memory. A Fenwick tree (binary indexed tree) is a smaller, simpler structure for prefix sums and point updates, also in O(log n). Use a Fenwick tree when its supported operations are sufficient.",
        ("segment", "fenwick", "tree", "range", "query", "fenwicktree"), ("segment tree", "fenwick tree", "binary indexed tree", "bit tree"),
    ),
    KnowledgeEntry(
        "What is disjoint set union (union-find)?",
        "Disjoint set union (DSU), also called union-find, tracks which items belong to the same connected component. `find(x)` gets a representative and `union(a, b)` merges sets. Path compression and union by size make operations nearly constant time in practice.",
        ("disjoint", "union", "find", "dsu", "component", "set"), ("disjoint set union", "union find", "union-find", "dsu"),
    ),
    KnowledgeEntry(
        "What is a monotonic stack or queue?",
        "A monotonic stack or deque keeps values in increasing or decreasing order by removing dominated values as new ones arrive. It can solve next-greater-element and sliding-window-extreme problems in O(n), because each item is added and removed at most once.",
        ("monotonic", "stack", "queue", "deque", "increasing", "decreasing"), ("monotonic stack", "monotonic queue", "monotonic stack queue"),
    ),
    KnowledgeEntry(
        "What is topological sorting?",
        "A topological ordering lists the vertices of a directed acyclic graph so every edge points forward. Use Kahn's algorithm with indegrees and a queue, or DFS postorder. If not all vertices are emitted, the graph contains a cycle.",
        ("topological", "sort", "sorting", "directed", "acyclic", "graph"), ("topological sort", "topological sorting"),
    ),
    KnowledgeEntry(
        "What is Dijkstra's algorithm?",
        "Dijkstra's algorithm finds shortest paths from one source when edge weights are nonnegative. A min-priority queue (Python's `heapq`) selects the next closest vertex. For negative edge weights, use an algorithm designed for them, such as Bellman-Ford.",
        ("dijkstra", "algorithm", "shortest", "path", "weight", "graph"), ("dijkstra algorithm", "dijkstra's algorithm", "shortest path"),
    ),
    KnowledgeEntry(
        "What is Prim's algorithm?",
        "Prim's algorithm builds a minimum spanning tree for a connected, weighted, undirected graph. Starting from one vertex, repeatedly add the lowest-weight edge that connects the tree to a new vertex. A min-heap helps select edges efficiently; negative edge weights are allowed.",
        ("prim", "minimum", "spanning", "tree", "weighted", "graph", "edge"), ("prim's algorithm", "minimum spanning tree", "mst"),
    ),
    KnowledgeEntry(
        "What is the Knight's Tour problem?",
        "The Knight's Tour asks for a sequence of chess-knight moves that visits every board square once. It can be modeled as a graph search: squares are vertices and legal moves are edges. Backtracking explores paths; move-ordering heuristics can reduce search, but do not change the need to verify a complete tour.",
        ("knight", "tour", "chess", "backtracking", "board", "move"), ("knight's tour", "knights tour"),
    ),
    KnowledgeEntry(
        "How can I solve a maze with search?",
        "Model open cells as positions and legal moves as edges. Use DFS or backtracking to find any path; use BFS when every move has equal cost and you need the shortest path. Keep a visited set and record parents if you need to reconstruct the route.",
        ("maze", "search", "path", "dfs", "bfs", "visited", "backtracking"), ("maze solving", "explore a maze"),
    ),
    KnowledgeEntry(
        "What is bit manipulation?",
        "Bit manipulation uses integer bitwise operators: `&` AND, `|` OR, `^` XOR, `~` NOT, `<<` left shift, and `>>` right shift. For example, `n & 1` checks whether a nonnegative integer is odd. Prefer clear code unless bit operations are useful for the task.",
        ("bit", "bits", "bitwise", "manipulation", "shift", "xor"), ("bit manipulation", "bitwise operations"),
    ),
    KnowledgeEntry(
        "What is KMP string search?",
        "Knuth-Morris-Pratt (KMP) searches for a pattern in text in O(n + m) time by reusing prefix-match information instead of restarting after every mismatch. It preprocesses a prefix table for the pattern. Python's `str.find()` is usually the practical choice unless implementing the algorithm for learning.",
        ("kmp", "knuth", "morris", "pratt", "pattern", "string", "search"), ("kmp algorithm", "knuth-morris-pratt"),
    ),
    KnowledgeEntry(
        "What is the Rabin-Karp algorithm?",
        "Rabin-Karp searches strings using a rolling hash to compare a pattern against text windows. It is O(n + m) on average, though hash collisions can require checking candidate matches and the worst case is slower. Python's `str.find()` is usually simpler for ordinary text search.",
        ("rabin", "karp", "rolling", "hash", "pattern", "string", "algorithm"), ("rabin-karp", "rabin karp algorithm"),
    ),
    KnowledgeEntry(
        "What are suffix trees and suffix arrays?",
        "A suffix array stores the sorted starting positions of every suffix of a string; it is a compact way to support substring queries. A suffix tree is a more memory-intensive compressed trie of suffixes. Python has no built-in implementation; both are specialized text-indexing structures.",
        ("suffix", "tree", "array", "string", "text", "index"), ("suffix tree", "suffix array", "suffix trees and suffix arrays"),
    ),
    KnowledgeEntry(
        "What is a Bloom filter?",
        "A Bloom filter is a compact probabilistic set-membership structure. It can say an item is definitely absent or probably present, but false positives are possible and false negatives are not (when used correctly). It does not store the original items and cannot delete safely without a counting variant.",
        ("bloom", "filter", "probabilistic", "membership", "false", "positive"), ("bloom filter",),
    ),
    KnowledgeEntry(
        "What is HyperLogLog?",
        "HyperLogLog estimates the number of distinct items in a large stream using very little memory. It is approximate, not an exact set, and is useful when the dataset is too large to retain every unique value. It is typically implemented with a specialized library or data service.",
        ("hyperloglog", "distinct", "cardinality", "estimate", "stream"), ("hyper log log", "hyperloglog"),
    ),
    KnowledgeEntry(
        "What is a Count-Min Sketch?",
        "A Count-Min Sketch is a compact probabilistic structure for estimating item frequencies in a stream. It can overestimate counts because of collisions, but does not underestimate them under the standard construction. It is useful for approximate heavy-hitter analysis.",
        ("count", "min", "sketch", "frequency", "stream", "estimate"), ("count-min sketch", "count min sketch"),
    ),
    KnowledgeEntry(
        "What is an AVL tree or red-black tree?",
        "AVL and red-black trees are self-balancing binary search trees. AVL trees keep stricter height balance, often making lookup shallower; red-black trees allow looser balance and have efficient updates. Both provide O(log n) search, insertion, and deletion. Python does not include either as a built-in container.",
        ("avl", "red", "black", "tree", "balance", "balanced"), ("avl tree", "red-black tree", "red black tree", "avl vs red-black"),
    ),
    KnowledgeEntry(
        "What are B-trees and B+ trees?",
        "B-trees are balanced multiway search trees designed to reduce disk or page reads. B+ trees keep records (or record pointers) in linked leaves, which makes range scans efficient. They are common in database and filesystem indexes; Python does not provide a built-in B-tree.",
        ("b", "tree", "trees", "btree", "bplus", "index", "database"), ("b-tree", "b trees", "b+ tree", "b+ trees"),
    ),
    KnowledgeEntry(
        "What are Tarjan's and Kosaraju's algorithms?",
        "Tarjan's and Kosaraju's algorithms find strongly connected components in a directed graph in O(V + E) time. Kosaraju uses two DFS passes and the reversed graph; Tarjan uses one DFS pass with low-link values and a stack.",
        ("tarjan", "kosaraju", "strongly", "connected", "component", "graph"), ("tarjan algorithm", "kosaraju algorithm", "tarjan and kosaraju"),
    ),
    KnowledgeEntry(
        "What is a network flow algorithm?",
        "A flow network is a directed graph with capacities; the max-flow problem finds the greatest flow from a source to a sink without exceeding capacities. Ford-Fulkerson augments paths in the residual graph; Dinic's algorithm uses level graphs and blocking flows and is often faster in practice.",
        ("network", "flow", "maxflow", "capacity", "residual", "source", "sink"), ("network flow", "maximum flow", "max flow"),
    ),
    KnowledgeEntry(
        "What are Ford-Fulkerson and Dinic's algorithms?",
        "Both solve maximum flow. Ford-Fulkerson repeatedly finds an augmenting path in the residual graph; its runtime depends on how paths are chosen and it can be problematic with irrational capacities. Dinic builds level graphs with BFS and sends blocking flows with DFS, giving stronger complexity bounds for many graph classes.",
        ("ford", "fulkerson", "dinic", "flow", "algorithm", "residual"), ("ford-fulkerson", "dinic algorithm", "dinic's algorithm"),
    ),
    KnowledgeEntry(
        "What are k-d trees, quadtrees, and octrees?",
        "A k-d tree partitions k-dimensional points using axis-aligned splits; quadtrees partition 2D space into four regions, and octrees partition 3D space into eight. They support spatial queries such as nearest-neighbor or region lookup, with performance depending on data and balance.",
        ("k", "d", "dimensional", "kd", "tree", "quadtree", "octree", "spatial", "region"), ("k-d tree", "kd tree", "k d tree", "quadtree", "octree", "k dimensional tree"),
    ),
    KnowledgeEntry(
        "What is an R-tree?",
        "An R-tree indexes spatial objects by grouping their bounding rectangles, making it useful for range and intersection queries on geographic or multidimensional data. It is commonly used in spatial databases and libraries; Python has no built-in R-tree container.",
        ("r", "tree", "spatial", "rectangle", "geographic", "index"), ("r-tree", "rtree", "r tree"),
    ),
    KnowledgeEntry(
        "What are skip lists?",
        "A skip list is a probabilistic ordered structure with multiple levels of forward links. Its search, insertion, and deletion take O(log n) expected time. It offers a simpler alternative to balanced trees in some systems, but Python has no built-in skip-list type.",
        ("skip", "list", "ordered", "level", "probabilistic"), ("skip list", "skip lists"),
    ),
    KnowledgeEntry(
        "What is an LSM tree?",
        "A log-structured merge tree (LSM tree) buffers writes in memory, then merges sorted runs on disk. It favors write throughput and is used by storage engines such as key-value databases. Reads may consult several levels, and compaction controls that cost.",
        ("lsm", "log", "structured", "merge", "tree", "storage", "database"), ("lsm tree", "log structured merge tree", "log-structured merge-tree"),
    ),
    KnowledgeEntry(
        "What is an abstract syntax tree (AST)?",
        "An abstract syntax tree represents source code as structured nodes such as expressions, calls, and statements. Python's `ast` module can parse and inspect Python source without executing it. ASTs are used by linters, formatters, compilers, and code-analysis tools.",
        ("abstract", "syntax", "tree", "ast", "parser", "source", "code"), ("abstract syntax tree", "ast"),
    ),
    KnowledgeEntry(
        "What are lexers, parsers, and parser combinators?",
        "A lexer turns characters into tokens; a parser turns tokens into a structured representation such as a syntax tree. Parser combinators build larger parsers by composing smaller ones. Python's `ast` module parses Python syntax, while libraries such as Lark or pyparsing can help parse custom languages.",
        ("lexer", "lexers", "parser", "parsers", "combinator", "token", "grammar"), ("lexer and parser", "parser combinators", "lexer parser combinators"),
    ),
    KnowledgeEntry(
        "What are lock-free data structures and compare-and-swap?",
        "Lock-free algorithms use atomic operations to make system-wide progress without ordinary locks. Compare-and-swap (CAS) atomically changes a value only if it still equals an expected value. Correct lock-free code is difficult and depends on memory-model guarantees; Python application code should usually use `threading` synchronization primitives.",
        ("lock", "free", "structure", "structures", "cas", "compare", "swap", "atomic"), ("lock-free", "lock free data structures", "compare and swap", "cas-based"),
    ),
    KnowledgeEntry(
        "What are cache-oblivious algorithms?",
        "Cache-oblivious algorithms are designed to use memory hierarchies efficiently without hard-coding a cache size or block size. Recursive divide-and-conquer layouts are common examples. They are an advanced performance topic; measure real workloads before choosing a specialized design.",
        ("cache", "oblivious", "algorithm", "memory", "hierarchy"), ("cache-oblivious algorithms", "cache oblivious"),
    ),
    KnowledgeEntry(
        "What are approximation algorithms?",
        "An approximation algorithm returns a solution with a provable quality bound when finding an exact optimum is too expensive. The approximation ratio compares its result with the optimal one. This is common for difficult optimization problems.",
        ("approximation", "algorithm", "approximate", "ratio", "optimization", "optimal"), ("approximation algorithms", "approximation algorithm"),
    ),
    KnowledgeEntry(
        "What are heuristics and metaheuristics?",
        "A heuristic is a practical rule that aims for a good solution without guaranteeing optimality. A metaheuristic, such as simulated annealing or a genetic algorithm, guides a broader search process. Evaluate solution quality and runtime on representative cases.",
        ("heuristic", "heuristics", "metaheuristic", "metaheuristics", "search", "optimization"), ("heuristics and metaheuristics", "metaheuristics"),
    ),
    KnowledgeEntry(
        "What is a dictionary?",
        "A dictionary stores key-value pairs. For example, `person = {\"name\": \"Ada\"}` and `person[\"name\"]` returns `\"Ada\"`. Use `person.get(\"age\")` when a key may be missing.",
        ("dictionary", "dict", "key", "value", "mapping"), ("key value", "hash map"),
    ),
    KnowledgeEntry(
        "How do for loops work?",
        "A `for` loop iterates over items in an iterable:\n\n```python\nfor item in [\"a\", \"b\"]:\n    print(item)\n```\nUse `range(n)` when you need a sequence of numbers.",
        ("for", "loop", "iterate", "iteration", "range"), ("repeat code", "iterate over"),
    ),
    KnowledgeEntry(
        "How do while loops work?",
        "A `while` loop repeats as long as its condition is true:\n\n```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1\n```\nMake sure the condition eventually becomes false to avoid an infinite loop.",
        ("while", "loop", "condition", "repeat"), ("while loop", "infinite loop"),
    ),
    KnowledgeEntry(
        "How do I handle exceptions?",
        "Use `try` and `except` to handle expected errors. Catch a specific exception when possible:\n\n```python\ntry:\n    number = int(text)\nexcept ValueError:\n    print(\"Please enter a whole number.\")\n```",
        ("exception", "error", "try", "except", "handling"), ("catch an error", "error handling"),
    ),
    KnowledgeEntry(
        "What are Python modules and imports?",
        "A module is a Python file that can be reused in another file. Load it with `import`, for example `import math` or `from pathlib import Path`.",
        ("module", "import", "package", "library"), ("use a library", "importing"),
    ),
    KnowledgeEntry(
        "How do I create a class?",
        "Define a class with `class`. The `__init__` method initializes each instance, and `self` refers to that instance:\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n```",
        ("class", "object", "oop", "init", "self", "instance"), ("object oriented", "create an object"),
    ),
    KnowledgeEntry(
        "What is a tuple?",
        "A tuple is an ordered, immutable collection. Write one with parentheses, for example `point = (3, 4)`. Tuples are useful for fixed groups of values.",
        ("tuple", "immutable", "parentheses"), ("tuples",),
    ),
    KnowledgeEntry(
        "How do I use a set?",
        "A set holds unique values and is useful for removing duplicates or checking membership. Create one with `colors = {\"red\", \"blue\"}`; use `set()` for an empty set.",
        ("set", "unique", "duplicate", "membership"), ("remove duplicates",),
    ),
    KnowledgeEntry(
        "How do I read a file?",
        "Use `open()` with a context manager so the file closes automatically:\n\n```python\nfrom pathlib import Path\ntext = Path(\"notes.txt\").read_text(encoding=\"utf-8\")\n```\nFor line-by-line processing, iterate over the opened file.",
        ("file", "read", "open", "path", "text"), ("read a file", "load a file"),
    ),
    KnowledgeEntry(
        "What is a list comprehension?",
        "A list comprehension builds a list from an iterable in a compact way. For example, `[n * n for n in range(5)]` produces `[0, 1, 4, 9, 16]`.",
        ("comprehension", "list", "compact", "square"), ("list comprehension",),
    ),
    KnowledgeEntry(
        "How do I install a Python package?",
        "Install packages with pip, preferably inside a virtual environment: `python -m venv .venv`, activate it, then run `python -m pip install package-name`.",
        ("install", "package", "pip", "venv", "virtual", "environment"), ("pip install", "add a library"),
    ),
    KnowledgeEntry(
        "How do I check a Python value's type?",
        "Call `type(value)` to inspect its type. For type checks in conditional code, `isinstance(value, SomeType)` is usually more flexible.",
        ("type", "typeof", "isinstance", "data type"), ("check the type",),
    ),
    KnowledgeEntry(
        "What is an integer in Python?",
        "An integer (`int`) is a whole number with no fractional part, such as `7`, `0`, or `-12`. Python integers can grow beyond fixed machine sizes. Convert compatible text with `int(\"42\")`.",
        ("int", "integer", "integers", "whole", "number", "numbers"), ("what is int", "python int", "integer type"),
    ),
    KnowledgeEntry(
        "What is a string in Python?",
        "A string (`str`) is text. Write it inside single or double quotes, for example `name = \"Ada\"`. Strings are immutable; use methods such as `name.upper()` to create a changed result. Convert a value to text with `str(value)`.",
        ("str", "string", "strings", "text", "character", "characters"), ("what is str", "python str", "string type"),
    ),
    KnowledgeEntry(
        "What is a float in Python?",
        "A float (`float`) represents a number with a decimal part, such as `3.14` or `-0.5`. For exact decimal arithmetic such as money, consider Python's `decimal.Decimal` instead.",
        ("float", "floats", "decimal", "fractional"), ("what is float", "floating point", "float type"),
    ),
    KnowledgeEntry(
        "What is a boolean in Python?",
        "A boolean (`bool`) represents a truth value: `True` or `False`. Comparisons such as `age >= 18` produce booleans, which are commonly used in `if` statements.",
        ("bool", "boolean", "booleans", "true", "false", "truth"), ("what is bool", "boolean type"),
    ),
    KnowledgeEntry(
        "What does None mean in Python?",
        "`None` represents the absence of a value. A function that reaches the end without a `return` statement returns `None`. Check it with `value is None`.",
        ("none", "null", "absence", "nothing"), ("what is none", "none type", "python null"),
    ),
    KnowledgeEntry("What is a variable?", "A variable is a name bound to a value. Assign with `=`: `score = 10`. Python is dynamically typed, so a name can later refer to a value of another type.", ("variable", "variables", "assignment", "assign", "name"), ("create a variable", "declare a variable")),
    KnowledgeEntry("How do comments work?", "Use `#` for a one-line comment. A docstring is a string at the start of a module, class, or function that documents its behavior.", ("comment", "comments", "docstring", "documentation"), ("write a comment", "document a function")),
    KnowledgeEntry("How do if, elif, and else work?", "Use `if` to run code conditionally, `elif` for another condition, and `else` as the fallback. Indent each block:\n\n```python\nif score >= 90:\n    grade = \"A\"\nelif score >= 80:\n    grade = \"B\"\nelse:\n    grade = \"Keep practicing\"\n```", ("if", "elif", "else", "conditional", "condition"), ("if statement", "conditional statement")),
    KnowledgeEntry("What do break and continue do?", "`break` exits the nearest loop. `continue` skips to the next iteration. Use them when they make loop logic clearer; a helper function can sometimes be easier to read.", ("break", "continue", "skip", "exit", "loop"), ("break a loop", "continue a loop")),
    KnowledgeEntry("How do enumerate and zip work?", "`enumerate(items)` gives each item with its index, and `zip(a, b)` pairs items from iterables:\n\n```python\nfor index, name in enumerate(names, start=1):\n    print(index, name)\n\nfor name, score in zip(names, scores):\n    print(name, score)\n```", ("enumerate", "zip", "index", "pair", "iterable"), ("loop with index", "pair two lists")),
    KnowledgeEntry("How do I unpack values?", "Unpacking assigns items from an iterable to multiple names: `x, y = (3, 4)`. Use `first, *middle, last = values` to capture remaining items in a list.", ("unpack", "unpacking", "starred", "multiple assignment"), ("unpack a list", "unpack a tuple")),
    KnowledgeEntry("What are *args and **kwargs?", "In a function definition, `*args` collects extra positional arguments into a tuple and `**kwargs` collects extra named arguments into a dictionary. Use these when a function truly needs a flexible signature.", ("args", "kwargs", "positional", "keyword", "argument"), ("variable arguments", "arbitrary arguments")),
    KnowledgeEntry("What is a lambda function?", "A `lambda` creates a small anonymous function with one expression, such as `key=lambda item: item[1]`. For logic with multiple steps or a meaningful name, use `def` instead.", ("lambda", "anonymous", "inline", "function"), ("lambda function", "anonymous function")),
    KnowledgeEntry("What is recursion?", "Recursion is when a function calls itself. It needs a base case that stops the calls. For many tasks, a loop is simpler and avoids Python's recursion depth limit.", ("recursion", "recursive", "base case", "stack"), ("recursive function", "function call itself")),
    KnowledgeEntry("What is variable scope?", "A name assigned inside a function is local to that function unless declared `global` or `nonlocal`. Prefer passing values in and returning results instead of changing global state.", ("scope", "local", "global", "nonlocal", "name"), ("variable scope", "local variable", "global variable")),
    KnowledgeEntry("What is a generator?", "A generator produces values lazily, one at a time, which can save memory. Write a generator function with `yield`, or use a generator expression like `(n * n for n in range(10))`.", ("generator", "generators", "yield", "lazy", "iteration"), ("generator expression", "yield keyword")),
    KnowledgeEntry("What is an iterator?", "An iterator yields values one at a time. `iter(value)` gets an iterator and `next(iterator)` retrieves its next value. `for` loops handle this protocol automatically.", ("iterator", "iterators", "iter", "next", "iteration"), ("iteration protocol", "iter function")),
    KnowledgeEntry("What is a decorator?", "A decorator wraps or changes a function or class. The `@decorator` syntax applies it when the function is defined. Decorators are useful for reusable behavior such as logging or authorization.", ("decorator", "decorators", "wrapper", "wrap", "at sign"), ("python decorator", "function decorator")),
    KnowledgeEntry("What is a context manager?", "A context manager handles setup and cleanup around a block. Use `with`, for example `with open(\"notes.txt\") as file:`. It ensures resources are released even if an error occurs.", ("context", "manager", "with", "cleanup", "resource"), ("context manager", "with statement")),
    KnowledgeEntry("What is a dataclass?", "`dataclasses.dataclass` generates common methods such as `__init__` and `__repr__` for a class that mainly stores data:\n\n```python\nfrom dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: float\n    y: float\n```", ("dataclass", "dataclasses", "boilerplate", "record"), ("data class", "dataclass decorator")),
    KnowledgeEntry("What is inheritance?", "Inheritance lets a class reuse or specialize another class. Put the parent in parentheses, then call `super().__init__(...)` when the child needs the parent's initialization. Prefer composition when objects simply need to work together.", ("inheritance", "subclass", "parent", "super", "child", "object"), ("class inheritance", "inherit from a class")),
    KnowledgeEntry("What is a property?", "`@property` lets an attribute-style access run getter logic. It can be useful for derived values or validation, but ordinary public attributes are simpler when no extra behavior is needed.", ("property", "getter", "setter", "attribute", "property decorator"), ("python property", "property decorator")),
    KnowledgeEntry("What are dunder methods?", "Dunder methods have double underscores, such as `__init__`, `__str__`, and `__len__`. Python calls them to support object setup, display, and built-in operations. Implement them to make custom objects behave naturally.", ("dunder", "magic", "special", "__init__", "__str__", "method"), ("magic methods", "special methods")),
    KnowledgeEntry("What are type hints?", "Type hints document expected types and help editors and static checkers. They do not usually enforce types at runtime:\n\n```python\ndef greet(name: str) -> str:\n    return f\"Hello, {name}\"\n```", ("typing", "hint", "hints", "annotation", "annotations", "type"), ("type annotation", "function annotation")),
    KnowledgeEntry("How do match and case work?", "`match` and `case` compare a value against patterns, available in Python 3.10 and newer. They can make structured branching clearer; use ordinary `if` statements for simple conditions.", ("match", "case", "pattern", "structural"), ("pattern matching", "match case")),
    KnowledgeEntry("How do I raise an exception?", "Use `raise` to signal an error. Choose a specific built-in exception or define a custom one by subclassing `Exception`. Include a message that explains what went wrong.", ("raise", "custom", "exception", "error"), ("raise an error", "custom exception")),
    KnowledgeEntry("How do I use logging?", "Use the standard `logging` module instead of `print()` for application diagnostics. It supports levels such as `DEBUG`, `INFO`, `WARNING`, and `ERROR`, and can send messages to a file or console.", ("logging", "log", "logger", "debug", "diagnostic"), ("logging module", "log an error")),
    KnowledgeEntry("How do I work with JSON?", "Use `json.loads(text)` to parse JSON text and `json.dumps(value)` to produce JSON text. With files, use `json.load(file)` and `json.dump(value, file)`. JSON supports a limited set of data types.", ("json", "serialize", "serialization", "parse", "loads", "dumps"), ("read json", "write json", "json file")),
    KnowledgeEntry("How do I work with CSV files?", "Use Python's `csv` module. `csv.reader` reads rows and `csv.DictReader` maps columns by header. Open files with `newline=\"\"` and a specified encoding to handle CSV consistently.", ("csv", "comma", "spreadsheet", "row", "column"), ("read csv", "write csv", "csv file")),
    KnowledgeEntry("How do I work with paths?", "Use `pathlib.Path` to build and inspect filesystem paths. For example, `Path(\"data\") / \"input.txt\"` joins path parts in a platform-aware way. `Path.read_text()` and `write_text()` handle simple text files.", ("pathlib", "path", "paths", "directory", "filesystem"), ("path object", "join file paths")),
    KnowledgeEntry("How do I use regular expressions?", "The `re` module searches text using patterns. `re.search()` finds a match, `re.findall()` returns matches, and `re.sub()` replaces them. For simple fixed text, ordinary string methods are easier to read.", ("regex", "regular", "expression", "pattern", "re."), ("regular expression", "regex pattern")),
    KnowledgeEntry("How do I work with dates and times?", "Use `datetime.date` and `datetime.datetime` for dates and times, and `datetime.timedelta` for durations. Attach a timezone when representing real-world instants; naive datetimes can be ambiguous.", ("datetime", "date", "time", "timezone", "timedelta"), ("date and time", "python dates")),
    KnowledgeEntry("How do I generate random values?", "Use `random` for simulations and casual selection, such as `random.choice(items)`. For security-sensitive tokens or passwords, use the `secrets` module instead.", ("random", "randomness", "choice", "shuffle", "secure", "secrets"), ("random number", "random values")),
    KnowledgeEntry("What is the collections module?", "`collections` provides useful container types: `Counter` counts items, `defaultdict` supplies missing values, `deque` supports fast operations at both ends, and `namedtuple` creates tuple-like records.", ("collections", "counter", "defaultdict", "deque", "namedtuple"), ("collections module", "count items")),
    KnowledgeEntry("What are itertools and functools?", "`itertools` offers efficient iterator building blocks such as `chain`, `product`, and `islice`. `functools` includes tools such as `lru_cache`, `partial`, and `reduce`. Both are part of the standard library.", ("itertools", "functools", "chain", "product", "lru_cache", "partial"), ("iterator tools", "cache a function")),
    KnowledgeEntry("How do I create a command-line argument parser?", "Use `argparse` to define command-line options, validate input, and generate help text. Create an `ArgumentParser`, add arguments, then call `parse_args()`.", ("argparse", "command", "line", "cli", "argument", "parser"), ("command line arguments", "cli arguments")),
    KnowledgeEntry("How do I use SQLite?", "Python includes the `sqlite3` module for local SQL databases. Use parameterized queries such as `connection.execute(\"SELECT ... WHERE id = ?\", (record_id,))`; never build SQL by concatenating untrusted input.", ("sqlite", "sqlite3", "sql", "database", "query"), ("sqlite database", "python database")),
    KnowledgeEntry("How do I make an HTTP request?", "For simple HTTP requests with no third-party dependencies, use `urllib.request`. For larger applications, popular packages such as `requests` can offer a friendlier interface. Handle timeouts and network errors.", ("http", "https", "request", "urllib", "api", "network"), ("http request", "call an api", "web request")),
    KnowledgeEntry("How do I use threads or processes?", "Threads are useful for I/O-bound work; processes can run CPU-bound Python work in parallel. The `threading` and `multiprocessing` modules provide these tools. Start with a simple sequential solution and measure before adding concurrency.", ("thread", "threading", "process", "multiprocessing", "parallel", "concurrency"), ("run in parallel", "concurrent tasks")),
    KnowledgeEntry("How do I use async and await?", "`async def` defines a coroutine, `await` pauses it until an asynchronous operation completes, and `asyncio` runs coroutines. Async is most useful for programs that wait on many network or other I/O operations.", ("async", "await", "asyncio", "coroutine", "asynchronous"), ("async function", "async programming")),
    KnowledgeEntry("How do I write tests?", "Python's standard library includes `unittest`. Write small tests for expected behavior and edge cases, then run them with `python -m unittest`. `pytest` is a popular third-party alternative with a simpler test syntax.", ("test", "tests", "testing", "unittest", "pytest", "assert"), ("write a test", "run tests", "unit test")),
    KnowledgeEntry("How do I debug Python code?", "Use the traceback to find the line where an error occurred. Add a focused test or inspect values with a debugger such as `pdb`; avoid leaving temporary prints in production code. Reproduce the smallest failing case first.", ("debug", "debugging", "traceback", "pdb", "error"), ("debug a program", "debug code")),
    KnowledgeEntry("How do I use a virtual environment?", "Create an isolated environment with `python -m venv .venv`, activate it for your shell, then install packages using `python -m pip install ...`. This keeps project dependencies separate from other Python projects.", ("venv", "virtual", "environment", "isolate", "activate"), ("virtualenv", "create an environment")),
    KnowledgeEntry("How do I manage Python dependencies?", "Install a package with `python -m pip install package-name`. Record dependencies in a project file such as `requirements.txt` or `pyproject.toml`, and use a virtual environment so installs stay isolated.", ("dependency", "dependencies", "requirements", "pyproject", "pip", "package"), ("requirements file", "manage packages")),
    KnowledgeEntry("What is PEP 8?", "PEP 8 is Python's style guide. It recommends consistent indentation, readable names, and formatting that makes code easy to scan. Many teams automate formatting and lint checks to apply shared conventions.", ("pep", "pep8", "style", "format", "lint", "readability"), ("python style guide", "code style")),
    KnowledgeEntry("What are Python's built-in functions?", "Python includes built-ins such as `len`, `range`, `sum`, `min`, `max`, `sorted`, `enumerate`, and `zip`. They are available without an import. Use `help(name)` or the official docs to explore one.", ("builtin", "builtins", "built-in", "function", "functions", "len", "sum"), ("built in functions", "python builtins")),
    KnowledgeEntry("How do I use map and filter?", "`map(function, values)` transforms each item, while `filter(function, values)` keeps items that pass a condition. List comprehensions are often more readable for simple cases.", ("map", "filter", "transform", "functional"), ("map function", "filter function")),
    KnowledgeEntry("What is a shallow or deep copy?", "Assignment creates another reference to the same object, not a copy. `copy.copy()` makes a shallow copy; `copy.deepcopy()` recursively copies nested objects. Prefer immutable values or explicit construction when that is clearer.", ("copy", "shallow", "deepcopy", "reference", "mutable"), ("deep copy", "shallow copy")),
    KnowledgeEntry("How does Python manage memory?", "Python manages object memory automatically, including reference counting and a garbage collector for reference cycles. Usually you should focus on releasing external resources with context managers rather than manually freeing objects.", ("memory", "garbage", "collector", "reference", "leak"), ("garbage collection", "memory management")),
    KnowledgeEntry("Is eval safe in Python?", "Avoid `eval()` and `exec()` on untrusted input: they can execute arbitrary Python code. Use safer parsers such as `json.loads()` for JSON or validate input against the exact format you expect.", ("eval", "exec", "security", "unsafe", "untrusted"), ("eval security", "execute a string")),
    KnowledgeEntry("How do I use Python's interactive shell?", "Run `python3` in a terminal to open the interactive interpreter, where you can try expressions one at a time. Use `help(str)` or `dir(object)` to explore. Exit with `exit()` or Ctrl+D on macOS/Linux.", ("interactive", "shell", "repl", "interpreter", "help"), ("python repl", "interactive interpreter")),
)

VISUALS_BY_QUESTION = {
    "How do I approach a data-structures problem?": "workflow",
    "What is an array in Python?": "array",
    "What is a hash table or map?": "hash-table",
    "How do I use a queue in Python?": "queue",
    "What is a deque?": "queue",
    "How do I make a circular queue?": "circular-queue",
    "How do I implement a stack?": "stack",
    "How can a stack evaluate a postfix expression?": "stack",
    "What is a linked list?": "linked-list",
    "What is a tree data structure?": "tree",
    "What is a binary search tree?": "bst",
    "What is a heap?": "heap",
    "How do I make a priority queue?": "heap",
    "What is a graph data structure?": "graph",
    "What is the difference between an adjacency list and matrix?": "graph",
    "What are BFS and DFS?": "graph-search",
    "What is Prim's algorithm?": "graph-search",
    "What is the Knight's Tour problem?": "graph-search",
    "How can I solve a maze with search?": "graph-search",
    "How do I traverse a tree?": "tree-traversal",
    "How does binary search work?": "binary-search",
    "What is searching in algorithms?": "search",
    "How do I sort values in Python?": "sorting",
    "How do common sorting algorithms compare?": "sorting",
    "What is merge sort?": "sorting",
    "What is quicksort?": "sorting",
    "What is insertion sort?": "sorting",
    "What is sequential or linear search?": "search",
    "What is Big O notation?": "complexity",
    "What is time complexity?": "complexity",
    "What is space complexity?": "complexity",
    "What are the two-pointer and sliding-window techniques?": "sliding-window",
    "What is dynamic programming?": "dynamic-programming",
    "What is backtracking?": "backtracking",
    "What is a trie?": "trie",
    "What are segment trees and Fenwick trees?": "range-trees",
    "What is disjoint set union (union-find)?": "union-find",
    "What is a monotonic stack or queue?": "monotonic",
    "What is topological sorting?": "topological",
    "What is Dijkstra's algorithm?": "dijkstra",
    "What is a Bloom filter?": "bloom-filter",
    "How do I check whether two strings are anagrams?": "anagram",
    "How do I check balanced parentheses?": "parentheses",
    "How do I find the shortest word ladder?": "word-ladder",
    "What is recursion?": "recursion",
}

STOP_WORDS = {"a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it", "of", "python", "the", "to", "what", "with", "you", "your"}


def normalize(text: str) -> list[str]:
    """Return lowercase words with common English plurals reduced to their base form."""
    words = re.findall(r"[a-z0-9_]+", text.lower())
    normalized = []
    for word in words:
        if word == "tries":
            word = "trie"
        elif len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 5 and word.endswith(("sses", "shes", "ches", "xes", "zes")):
            word = word[:-2]
        elif len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
            word = word[:-1]
        normalized.append(word)
    return normalized


def find_entry(question: str) -> KnowledgeEntry | None:
    """Find the best matching knowledge entry using phrase and keyword scoring."""
    words = set(normalize(question)) - STOP_WORDS
    if not words:
        if "python" in normalize(question):
            return next(entry for entry in KNOWLEDGE_BASE if entry.question == "What is Python?")
        return None

    question_normalized = " ".join(normalize(question))
    best_entry: KnowledgeEntry | None = None
    best_score = 0.0

    for entry in KNOWLEDGE_BASE:
        keywords = set(entry.keywords)
        exact_overlap = words & keywords
        overlap = set(exact_overlap)
        # Allow a small typo only when the question already has an exact topic
        # match. This keeps fuzzy matching from inventing a topic from one word.
        if exact_overlap:
            for word in words - exact_overlap:
                if len(word) >= 6:
                    close = get_close_matches(word, [key for key in keywords if len(key) >= 6], n=1, cutoff=0.82)
                    if close:
                        overlap.add(close[0])
        score = len(overlap) / max(1, len(words))
        # Prefer entries whose title names the requested topic. This prevents a
        # broad keyword (for example, "graph") in an example problem such as
        # word ladder from winning over the graph overview itself.
        title_words = set(normalize(entry.question)) - STOP_WORDS
        score += 0.2 * len(words & title_words) / max(1, len(words))
        for phrase in entry.aliases:
            phrase_words = " ".join(normalize(phrase))
            if phrase_words and phrase_words in question_normalized:
                score += 1.0
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry if best_entry is not None and best_score >= 0.25 else None


def find_answer(question: str) -> str:
    """Return an answer for a question, with a useful fallback when unmatched."""
    entry = find_entry(question)
    if entry:
        return entry.answer
    if not set(normalize(question)) - STOP_WORDS:
        return "Please ask a Python question, such as ‘How do I define a function?’"
    return ("I don't have a confident answer for that yet. I can help with Python built-in types, data structures, "
            "algorithms, complexity, problem solving, functions, collections, loops, exceptions, modules, classes, files, and packages. "
            "Try asking about one of those topics.")


def main() -> None:
    print("Python Q&A Chatbot")
    print("Ask a Python question, or type 'quit' to exit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break
        if question.lower() in {"quit", "exit", "q"}:
            print("Bot: Goodbye!")
            break
        print(f"Bot: {find_answer(question)}\n")


if __name__ == "__main__":
    main()
