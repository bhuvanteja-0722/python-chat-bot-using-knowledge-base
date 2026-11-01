"""A small command-line Python question-answering chatbot."""

from __future__ import annotations

import re
from difflib import get_close_matches
from dataclasses import dataclass
from knowledge_expansion import ADDITIONAL_KNOWLEDGE
from api_knowledge import API_KNOWLEDGE


@dataclass(frozen=True)
class KnowledgeEntry:
    question: str
    answer: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    exact_only: bool = False


KNOWLEDGE_BASE = (
    KnowledgeEntry(
        "What is Python?",
        "Python is a high-level, general-purpose programming language known for readable syntax and a large standard library.",
        ("language",), ("what is python", "about python"),
    ),
    KnowledgeEntry(
        "What are the drawbacks of Python?",
        "Python has a few trade-offs: it is often slower than compiled languages such as C or Rust for CPU-heavy work; its dynamic typing can let some errors appear only at runtime; and its memory use can be higher than lower-level languages. It can also be a poor fit for some mobile, embedded, or browser-native applications. For many projects, clear code and fast development outweigh these costs. Use profiling before optimizing, add type hints and tests, and move proven hotspots to optimized libraries or compiled extensions when needed.",
        ("drawback", "disadvantage", "limitation", "slow", "performance", "memory", "typing", "python"),
        ("drawbacks of python", "disadvantages of python", "limitations of python", "cons of python", "downsides of python", "problems with python"),
    ),
    KnowledgeEntry(
        "What are the advantages of Python?",
        "Python is popular because its syntax is readable, it supports several programming styles, and its standard library and package ecosystem cover many tasks. It works well for scripting, web services, automation, data analysis, and machine learning. Its trade-offs include slower execution than many compiled languages for some workloads, so choose based on the project rather than popularity alone.",
        ("advantage", "benefit", "strength", "popular", "python", "readable", "library", "ecosystem"),
        ("advantages of python", "benefits of python", "pros of python", "why is python popular", "why use python"),
    ),
    KnowledgeEntry(
        "Why can Python be slower than compiled languages?",
        "In common implementations such as CPython, Python bytecode is interpreted by a virtual machine and dynamic operations add runtime work. This can make tight, CPU-heavy loops slower than equivalent compiled code. Many Python libraries avoid that cost by doing intensive work in optimized C, C++, or Fortran code. Measure with a profiler first; then improve the algorithm, use vectorized libraries, or compile only proven hot spots.",
        ("python", "slow", "slower", "performance", "compiled", "interpreted", "speed", "cpython"),
        ("why is python slow", "python performance", "python speed", "python slower than c", "why python is slower than compiled languages"),
    ),
    KnowledgeEntry(
        "What is Python commonly used for?",
        "Python is used for automation and scripting, web backends and APIs, data analysis, scientific computing, machine learning, testing, and general-purpose applications. Its broad package ecosystem helps teams build these quickly. The best language still depends on requirements such as runtime speed, platform, deployment, and team experience.",
        ("python", "use", "uses", "application", "automation", "web", "data", "machine", "learning"),
        ("uses of python", "what can python do", "what is python used for", "python use cases", "applications of python"),
    ),
    KnowledgeEntry(
        "Is Python interpreted or compiled?",
        "It depends on the implementation. CPython, the most widely used implementation, compiles source code to bytecode and executes that bytecode in a virtual machine; this is why Python is commonly called interpreted. Other implementations may work differently. You usually run a `.py` program directly with `python file.py` without managing the bytecode yourself.",
        ("python", "interpreted", "compiled", "bytecode", "implementation", "cpython"),
        ("is python interpreted", "is python compiled", "python compiler or interpreter", "how python runs"),
    ),
    KnowledgeEntry(
        "Is Python a good language for beginners?",
        "Python is often a good first language because its syntax is relatively readable and it lets beginners practice core ideas such as variables, conditions, loops, and functions without much setup. It is still a real programming language: learning debugging, data structures, testing, and how programs run takes practice. Start with small programs and build them up.",
        ("python", "beginner", "learn", "first", "easy", "start"),
        ("is python good for beginners", "is python easy to learn", "should i learn python first", "python for beginners"),
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
        "What does Python's map() function do?",
        "`map(function, iterable)` applies a function to each item and returns a lazy iterator. For example, `list(map(str.upper, [\"a\", \"b\"]))` gives `[\"A\", \"B\"]`. A list comprehension is often easier to read for simple transformations.",
        ("map", "function", "iterable", "transform", "lazy", "built-in"), ("map function", "map() function", "python map function", "python's map", "python map", "map in python"),
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
        ("tree", "node", "root", "child", "parent", "hierarchy"), ("tree", "tree data structure", "binary tree"),
    ),
    KnowledgeEntry(
        "What is a binary tree?",
        "A binary tree is a tree where each node has at most two children, commonly called left and right. It is a structure, not automatically a search tree: a binary search tree adds an ordering rule. Python has no built-in binary-tree container, so nodes are commonly modeled with a class or dataclass.",
        ("binary", "tree", "left", "right", "child", "children"), ("binary tree", "binary trees"),
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
        "How do I find a shortest path in an unweighted graph?",
        "Use breadth-first search (BFS): mark the start as visited, then explore neighbors with a `deque`. The first time BFS reaches a vertex, it has found a path with the fewest edges. Store each vertex's parent if you need to reconstruct the route. This takes O(V + E) time with an adjacency list.",
        ("shortest", "path", "unweighted", "graph", "bfs", "breadth", "deque", "parent"), ("shortest path in an unweighted graph", "unweighted shortest path", "bfs shortest path"),
    ),
    KnowledgeEntry(
        "How do I choose a shortest-path algorithm?",
        "Choose by edge weights: BFS finds paths with the fewest edges in an unweighted graph; Dijkstra handles nonnegative weights; Bellman-Ford supports negative weights and can detect a reachable negative cycle. For all-pairs distances on a small dense graph, Floyd-Warshall is another option.",
        ("shortest", "path", "graph", "weight", "bfs", "dijkstra", "bellman", "floyd"), ("shortest path", "find a shortest path", "shortest paths in a graph"),
    ),
    KnowledgeEntry(
        "How do I solve the Two Sum problem?",
        """Scan the numbers once while storing values already seen. For each number, check whether its complement (`target - number`) is in a dictionary; if so, return the two indices. This takes O(n) average time and O(n) extra space:

```python
def two_sum(nums, target):
    seen = {}
    for i, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return seen[complement], i
        seen[value] = i
    return None
```""",
        ("two", "sum", "target", "complement", "indices", "dictionary", "hash"), ("two-sum", "two sum problem", "find two numbers that add to a target"),
    ),
    KnowledgeEntry(
        "How do prefix sums work?",
        "A prefix-sum array stores cumulative totals so a range sum can be answered with two lookups. Let `prefix[0] = 0` and `prefix[i + 1] = prefix[i] + values[i]`; then the sum from index `left` through `right` is `prefix[right + 1] - prefix[left]`. Building it takes O(n), and each range query takes O(1).",
        ("prefix", "sum", "range", "cumulative", "array", "query"), ("prefix sum", "prefix sums", "range sum queries"),
    ),
    KnowledgeEntry(
        "How do I merge overlapping intervals?",
        """Sort intervals by start, then merge each interval into the previous one when they overlap. Sorting dominates the cost, so this is O(n log n):

```python
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```""",
        ("merge", "interval", "overlap", "range", "sort"), ("merge intervals", "merge overlapping intervals", "interval merging"),
    ),
    KnowledgeEntry(
        "How do I find the kth largest value?",
        "For a small k, keep a min-heap of at most k values; its root is the kth largest after the scan. This takes O(n log k) time and O(k) space. Python's `heapq.nlargest(k, values)[-1]` is convenient when k is valid and the input is nonempty.",
        ("kth", "largest", "smallest", "heap", "priority", "selection", "top"), ("k-th largest", "kth largest element", "find the kth largest"),
    ),
    KnowledgeEntry(
        "How can I detect a cycle in a linked list?",
        "Floyd's tortoise-and-hare algorithm uses two references: move `slow` one node and `fast` two nodes at a time. If they meet, there is a cycle; if `fast` reaches `None`, there is not. It takes O(n) time and O(1) extra space.",
        ("cycle", "linked", "list", "floyd", "tortoise", "hare", "slow", "fast"), ("linked list cycle", "detect a cycle in a linked list", "cycle detection in linked list"),
    ),
    KnowledgeEntry(
        "How does binary search work?",
        "Binary search finds a value in a sorted sequence by repeatedly halving the search range, taking O(log n) comparisons. The input must already be sorted. Python's `bisect` module provides insertion-point searches for sorted lists.",
        ("binary", "search", "sorted", "bisect", "logarithmic"), ("binary search",),
    ),
    KnowledgeEntry(
        "What is searching in algorithms?",
        "Searching finds an item or position. A linear scan works on any iterable and takes O(n); binary search takes O(log n) but requires sorted data. For repeated membership checks, a set or dictionary usually offers O(1) average lookup.",
        ("searching", "search", "find", "lookup", "linear", "algorithm"), ("search algorithms", "searching algorithms"),
    ),
    KnowledgeEntry(
        "How do I sort values in Python?",
        "Use `sorted(values)` to make a new sorted list or `values.sort()` to sort a list in place. Pass `key=` to choose what to compare, and `reverse=True` for descending order. Python's sort is stable.",
        ("sort", "sorting", "sorted", "order", "key", "reverse"), ("sorting a list", "sort values in python"),
    ),
    KnowledgeEntry(
        "How do common sorting algorithms compare?",
        "Bubble, selection, and insertion sort are usually O(n²); insertion sort can be useful on small or nearly sorted inputs. Merge sort is O(n log n), stable, and uses extra memory. Quicksort is O(n log n) on average but O(n²) in the worst case. In real Python code, prefer the stable built-in `sorted()` unless you are studying or need a special algorithm.",
        ("sorting", "algorithm", "bubble", "selection", "insertion", "merge", "quick", "compare"), ("sorting algorithms", "compare sorting methods", "sorting methods"),
    ),
    KnowledgeEntry(
        "What is merge sort?",
        "Merge sort divides a sequence into halves, sorts each half, then merges them. It runs in O(n log n) time and is stable, with O(n) extra memory for the usual array implementation.",
        ("merge", "sort", "sorting", "divide", "conquer"), ("merge sort algorithm",),
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
        ("big", "o", "notation", "asymptotic", "algorithm"), ("big o notation", "big-o notation", "order of growth", "complexity analysis"),
    ),
    KnowledgeEntry(
        "What is complexity analysis?",
        "Complexity analysis estimates how an algorithm's time and extra memory grow with input size. Big O summarizes the growth rate; time complexity measures work, while space complexity measures memory. State assumptions and check the dominant operations rather than treating Big O as elapsed seconds.",
        ("complexity", "analysis", "time", "space", "growth", "algorithm"), ("analyze complexity", "algorithm complexity analysis"),
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
        ("dijkstra", "algorithm", "shortest", "path", "weight", "graph"), ("dijkstra algorithm", "dijkstra's algorithm", "shortest path with nonnegative weights"),
    ),
    KnowledgeEntry(
        "What is the Bellman-Ford algorithm?",
        "Bellman-Ford finds single-source shortest paths even when some edge weights are negative. It relaxes every edge up to V − 1 times, then checks once more for a reachable negative cycle. Its O(VE) running time is usually slower than Dijkstra on nonnegative graphs.",
        ("bellman", "ford", "shortest", "path", "negative", "weight", "cycle"), ("bellman ford", "bellman-ford algorithm", "negative-weight shortest paths"),
    ),
    KnowledgeEntry(
        "What is the Floyd-Warshall algorithm?",
        "Floyd-Warshall computes shortest-path distances between every pair of vertices. It incrementally allows each vertex as an intermediate stop, using O(V³) time and O(V²) space. It supports negative edges, but a negative cycle means finite shortest paths are not defined for affected pairs.",
        ("floyd", "warshall", "all", "pairs", "shortest", "path", "distance", "graph"), ("floyd-warshall", "floyd warshall algorithm", "all-pairs shortest paths"),
    ),
    KnowledgeEntry(
        "What is counting sort or radix sort?",
        "Counting sort counts occurrences and is useful when integer keys come from a reasonably small range; its time and memory depend on that range. Radix sort orders values digit by digit and can be linear in the number of items times the digit count. They avoid comparison sorting's general O(n log n) bound by using assumptions about the keys.",
        ("counting", "radix", "sort", "sorting", "integer", "digit", "count"), ("counting sort", "radix sort", "non-comparison sorting"),
    ),
    KnowledgeEntry(
        "What is quickselect?",
        "Quickselect partitions around a pivot like quicksort but continues only in the partition containing the requested rank. It finds the kth smallest or largest item in O(n) expected time, though O(n²) is possible in the worst case. Python's `heapq` is often simpler for small k.",
        ("quickselect", "selection", "kth", "partition", "pivot", "largest", "smallest"), ("quick select", "kth selection", "selection algorithm"),
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
        "What is branch and bound?",
        "Branch and bound searches a decision tree of candidate solutions. It keeps the best complete solution found so far and uses bounds to prune branches that cannot beat it. It can solve exact optimization problems, though worst-case runtime may still be exponential.",
        ("branch", "bound", "optimization", "prune", "search", "decision"), ("branch-and-bound", "branch and bound algorithm"),
    ),
    KnowledgeEntry(
        "What is a randomized algorithm?",
        "A randomized algorithm uses random choices while it runs. A Las Vegas algorithm always returns a correct answer but has variable runtime; a Monte Carlo algorithm has a bounded runtime but a small probability of error. Random pivots can improve quicksort's expected behavior, and reservoir sampling selects from a stream with limited memory.",
        ("randomized", "random", "probability", "randomness", "monte", "carlo", "las", "vegas", "algorithm"), ("randomized algorithms", "random algorithm"),
    ),
    KnowledgeEntry(
        "What does NP-hard mean?",
        "An NP-hard problem is at least as difficult as every problem in NP under polynomial-time reductions. NP-complete problems are both in NP and NP-hard. These labels do not prove that every instance is slow, but no polynomial-time exact algorithm is known for the general cases; practical solvers use special cases, heuristics, or approximation methods.",
        ("np", "hard", "complete", "complexity", "reduction", "polynomial"), ("np-hard", "np hard problem", "np-complete"),
    ),
    KnowledgeEntry(
        "What is A* search?",
        "A* finds a low-cost path using priority f(n) = g(n) + h(n): g is the cost so far and h estimates the remaining cost. With a suitable admissible heuristic, A* returns an optimal path; its memory use can be large. It is used for route finding and puzzles.",
        ("a", "star", "astar", "search", "heuristic", "path", "shortest", "priority"), ("a-star search", "a* search", "astar search", "a star algorithm"),
    ),
    KnowledgeEntry(
        "What is Kruskal's algorithm?",
        "Kruskal's algorithm builds a minimum spanning forest by sorting edges by weight and adding an edge only when it joins two different components. A disjoint-set (union-find) structure detects cycles efficiently. For a connected graph, the result is a minimum spanning tree.",
        ("kruskal", "minimum", "spanning", "tree", "edge", "weight", "union", "find"), ("kruskal algorithm", "kruskal's algorithm", "minimum spanning tree kruskal"),
    ),
    KnowledgeEntry(
        "How do I sort a dictionary in Python?",
        "A dictionary preserves insertion order, but you can create a sorted list of its keys or items. Sort by key with `sorted(data.items())`, or by value with `sorted(data.items(), key=lambda item: item[1])`. Wrap the result with `dict(...)` if you need a new dictionary in that order.",
        ("sort", "sorting", "dictionary", "dict", "key", "value", "items"), ("sort a dictionary", "sort dictionary by value", "sort dictionary by key"),
    ),
    KnowledgeEntry(
        "What is the difference between a list and a tuple?",
        "Both are ordered sequences. A list is mutable (`[1, 2]`), so items can be added or changed; a tuple is immutable (`(1, 2)`) and suits fixed groups of values. Both support indexing and iteration. Choose based on whether the collection should change, not on a guaranteed speed advantage.",
        ("difference", "list", "tuple", "mutable", "immutable", "sequence"), ("list vs tuple", "list and tuple difference", "difference between list and tuple"),
    ),
    KnowledgeEntry(
        "What are heuristics and metaheuristics?",
        "A heuristic is a practical rule that aims for a good solution without guaranteeing optimality. A metaheuristic, such as simulated annealing or a genetic algorithm, guides a broader search process. Evaluate solution quality and runtime on representative cases.",
        ("heuristic", "heuristics", "metaheuristic", "metaheuristics", "search", "optimization"), ("heuristics and metaheuristics", "metaheuristics"),
    ),
    KnowledgeEntry(
        "What is a dictionary?",
        "A dictionary stores key-value pairs. For example, `person = {\"name\": \"Ada\"}` and `person[\"name\"]` returns `\"Ada\"`. Use `person.get(\"age\")` when a key may be missing.",
        ("dictionary", "dict", "key", "value", "mapping"), ("dictionary", "key value", "hash map"),
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
        ("str", "string", "strings", "text", "character", "characters"), ("what is str", "python str", "string type", "string", "strings"),
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
    KnowledgeEntry("How do match and case work?", "`match` and `case` compare a value against patterns, available in Python 3.10 and newer. They can make structured branching clearer; use ordinary `if` statements for simple conditions.", ("match", "case", "pattern", "structural"), ("pattern matching",)),
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
    KnowledgeEntry(
        "How do I implement binary search in Python?",
        "Binary search needs sorted data. Keep a half-open search interval `[left, right)`; this lower-bound version returns the first index whose value is at least the target, or `len(values)` if none exists:\n\n```python\ndef lower_bound(values, target):\n    left, right = 0, len(values)\n    while left < right:\n        middle = (left + right) // 2\n        if values[middle] < target:\n            left = middle + 1\n        else:\n            right = middle\n    return left\n```\nIt takes O(log n) time.",
        ("binary", "search", "implement", "implementation", "code", "lower", "bound", "sorted", "python"), ("binary search implementation", "binary search code", "write binary search in python", "lower bound search", "implement binary search"),
    ),
    KnowledgeEntry(
        "How do I implement Dijkstra's algorithm in Python?",
        "Represent a weighted graph as `node: [(neighbor, weight), ...]`. Use a min-heap, ignore stale heap entries, and only use Dijkstra when all weights are nonnegative:\n\n```python\nfrom heapq import heappop, heappush\nfrom itertools import count\n\ndef dijkstra(graph, source):\n    distances = {source: 0}\n    order = count()\n    heap = [(0, next(order), source)]\n    while heap:\n        distance, _, node = heappop(heap)\n        if distance != distances[node]:\n            continue\n        for neighbor, weight in graph.get(node, []):\n            candidate = distance + weight\n            if candidate < distances.get(neighbor, float('inf')):\n                distances[neighbor] = candidate\n                heappush(heap, (candidate, next(order), neighbor))\n    return distances\n```",
        ("dijkstra", "implement", "implementation", "code", "python", "heap", "weighted", "distance", "shortest"), ("dijkstra implementation", "dijkstra code", "write dijkstra in python", "implement dijkstra"),
    ),
    KnowledgeEntry(
        "How do I implement topological sorting in Python?",
        "Kahn's algorithm repeatedly emits vertices with indegree zero. If fewer than all vertices are emitted, the graph has a cycle and is not a DAG:\n\n```python\nfrom collections import deque\n\ndef topological_order(graph):\n    nodes = set(graph)\n    for neighbors in graph.values():\n        nodes.update(neighbors)\n    indegree = {node: 0 for node in nodes}\n    for neighbors in graph.values():\n        for neighbor in neighbors:\n            indegree[neighbor] += 1\n    ready = deque(node for node in nodes if indegree[node] == 0)\n    order = []\n    while ready:\n        node = ready.popleft()\n        order.append(node)\n        for neighbor in graph.get(node, []):\n            indegree[neighbor] -= 1\n            if indegree[neighbor] == 0:\n                ready.append(neighbor)\n    if len(order) != len(nodes):\n        raise ValueError('graph contains a cycle')\n    return order\n```",
        ("topological", "sort", "sorting", "implement", "implementation", "code", "python", "kahn", "dag", "indegree"), ("topological sort implementation", "topological sorting code", "kahn's algorithm in python", "implement topological sorting"),
    ),
    KnowledgeEntry(
        "How do I implement union-find in Python?",
        "Store a parent and component size for each item. Path halving compresses paths during `find`; union by size keeps trees shallow. Operations are nearly constant amortized time:\n\n```python\nclass DisjointSet:\n    def __init__(self, n):\n        self.parent = list(range(n))\n        self.size = [1] * n\n\n    def find(self, x):\n        while x != self.parent[x]:\n            self.parent[x] = self.parent[self.parent[x]]\n            x = self.parent[x]\n        return x\n\n    def union(self, a, b):\n        a, b = self.find(a), self.find(b)\n        if a == b:\n            return False\n        if self.size[a] < self.size[b]:\n            a, b = b, a\n        self.parent[b] = a\n        self.size[a] += self.size[b]\n        return True\n```",
        ("union", "find", "dsu", "disjoint", "implement", "implementation", "code", "python", "parent", "component"), ("union-find implementation", "disjoint set code", "implement dsu in python", "implement union-find"),
    ),
    KnowledgeEntry(
        "How do I generate all subsets with backtracking?",
        "At each position, choose to exclude or include the item, then undo the choice before exploring the next branch. There are 2ⁿ subsets, so outputting them already takes O(n·2ⁿ) total time:\n\n```python\ndef subsets(values):\n    result, chosen = [], []\n\n    def visit(index):\n        if index == len(values):\n            result.append(chosen.copy())\n            return\n        visit(index + 1)\n        chosen.append(values[index])\n        visit(index + 1)\n        chosen.pop()\n\n    visit(0)\n    return result\n```",
        ("subset", "subsets", "backtracking", "generate", "combination", "include", "exclude", "recursion"), ("generate all subsets", "subsets with backtracking", "power set in python"),
    ),
    KnowledgeEntry(
        "How do I find the longest palindromic substring?",
        "Expand around every possible center. There are centers between characters and on characters because palindromes can have even or odd length. Each expansion checks equal characters; the simple method takes O(n²) time and O(1) extra space.",
        ("longest", "palindrome", "palindromic", "substring", "expand", "center", "string"), ("longest palindrome substring", "longest palindromic substring", "palindrome substring problem"),
    ),
    KnowledgeEntry(
        "What does if __name__ == '__main__' do?",
        "A module's `__name__` is set to `'__main__'` when that file is run directly, and to its module name when imported. Put command-line startup code inside `if __name__ == '__main__':` so importing the module does not run the program automatically.",
        ("name", "main", "module", "script", "import", "run", "guard"), ("name main guard", "main guard in python", "if name main"),
    ),
    KnowledgeEntry(
        "How do I profile Python performance?",
        "Measure before optimizing. Use `timeit` for a small expression or benchmark, and `python -m cProfile -s cumulative your_script.py` to find where a whole program spends time. Profile representative inputs; a faster microbenchmark may not improve the real workload.",
        ("profile", "profiling", "performance", "timeit", "cprofile", "benchmark", "optimize"), ("profile python code", "measure python performance", "cprofile python"),
    ),
    KnowledgeEntry(
        "What is the Python GIL?",
        "In a standard GIL-enabled CPython build, the Global Interpreter Lock allows only one thread at a time to execute Python bytecode. Threads can still help I/O-bound tasks because they wait concurrently; CPU-heavy Python work often benefits more from processes or native code that releases the GIL. Free-threaded Python builds have different behavior.",
        ("gil", "global", "interpreter", "lock", "thread", "cpu", "io", "parallelism"), ("global interpreter lock", "python threads gil", "gil in python"),
    ),
    KnowledgeEntry(
        "How do I create a trie in Python?",
        "A trie stores characters along paths and shares common prefixes. Represent a node as a dictionary of child characters and reserve a marker such as `None` for end-of-word. Insert each character in turn; exact lookup follows the same path and checks the marker, while prefix lookup only needs to reach the final prefix node. Operations take O(L) time for a word of length L.",
        ("trie", "implement", "create", "python", "prefix", "insert", "lookup", "search"), ("trie implementation", "implement a trie", "trie data structure code"),
    ),
    KnowledgeEntry(
        "How do I implement an LRU cache in Python?",
        "`collections.OrderedDict` supports a simple least-recently-used cache: on access, call `move_to_end(key)`; after inserting, if capacity is exceeded call `popitem(last=False)`. For function-result caching, prefer `functools.lru_cache` when it fits the use case.",
        ("lru", "cache", "least", "recently", "used", "ordered", "implement", "python", "evict"), ("lru cache implementation", "implement an lru cache", "least recently used cache"),
    ),
    KnowledgeEntry(
        "How do I calculate the height of a binary tree?",
        "First choose a convention. Counting nodes, an empty tree has height 0 and a leaf has height 1; recursively, `height(node) = 1 + max(height(node.left), height(node.right))`. This visits each node once, so it takes O(n) time and O(h) call-stack space for tree height h.",
        ("height", "depth", "binary", "tree", "calculate", "recursive", "node"), ("binary tree height", "height of a binary tree", "maximum depth of a binary tree"),
    ),
    KnowledgeEntry(
        "How do I detect a cycle in an undirected graph?",
        "Run DFS from every unvisited vertex. During DFS, an edge to an already visited vertex indicates a cycle if it is not the edge back to the current node's parent. This takes O(V + E) time with an adjacency list; for multigraphs, track parent edge IDs rather than only parent vertices.",
        ("cycle", "detect", "undirected", "graph", "dfs", "visited", "parent"), ("undirected graph cycle", "cycle in an undirected graph", "detect cycle in undirected graph"),
    ),
    KnowledgeEntry(
        "How do I sum every fixed-size sliding window?",
        "Compute the first window sum once. For each next window, subtract the outgoing item and add the incoming item, so each update takes O(1) and all windows take O(n): `current += values[right] - values[right - k]`. Check that `k` is positive and no larger than the input length.",
        ("fixed", "size", "sliding", "window", "sum", "range", "array"), ("fixed-size sliding window", "fixed window sum", "sum of each window"),
    ),
    KnowledgeEntry(
        "How do I count paths through a grid with obstacles?",
        "Use dynamic programming: ways to reach a cell equal the ways from above plus the ways from the left; an obstacle contributes zero. A one-dimensional row array uses O(columns) space and O(rows × columns) time. Define whether diagonal moves are allowed before implementing it.",
        ("grid", "path", "paths", "obstacle", "dynamic", "programming", "ways", "count"), ("unique paths with obstacles", "grid paths dynamic programming", "count paths in a grid"),
    ),
    KnowledgeEntry(
        "How do I write a custom context manager?",
        "For a generator-based context manager, use `contextlib.contextmanager`: acquire the resource before `yield`, and release it in a `finally` block after `yield`. For classes, implement `__enter__` and `__exit__`. Prefer `with` blocks so cleanup happens even if the body raises an exception.",
        ("custom", "context", "manager", "contextmanager", "yield", "resource", "close"), ("write a context manager", "custom context manager", "contextmanager decorator"),
    ),
    KnowledgeEntry(
        "What do else and finally do in try/except?",
        "The `else` block runs only when the `try` block finishes without an exception. The `finally` block runs whether an exception happened or not, so it is useful for cleanup. A `with` statement is usually preferable for standard resources such as files and locks.",
        ("else", "finally", "try", "except", "exception", "cleanup", "error"), ("try except else finally", "finally block", "else block in try"),
    ),
    KnowledgeEntry(
        "What are positional-only and keyword-only arguments?",
        "In a function signature, `/` marks parameters that must be passed positionally, and `*` marks parameters that must be passed by keyword. For example, `def scale(value, /, factor=1, *, rounded=False): ...` makes `value` positional-only and `rounded` keyword-only. This can make APIs clearer and easier to evolve.",
        ("positional", "keyword", "only", "argument", "parameter", "slash", "asterisk", "signature"), ("keyword-only arguments", "positional-only arguments", "positional and keyword-only parameters"),
    ),
    KnowledgeEntry(
        "How do I run async tasks concurrently with asyncio.gather?",
        "Create coroutine objects and await `asyncio.gather(coro_one(), coro_two())` to run them concurrently on the event loop. This is useful for I/O-bound work; it does not make CPU-bound Python code execute in parallel by itself. Use `asyncio.run(main())` at a synchronous program entry point.",
        ("asyncio", "gather", "async", "tasks", "concurrent", "coroutine", "await"), ("asyncio gather", "run coroutines concurrently", "gather async tasks"),
    ),
    KnowledgeEntry(
        "What is the difference between str and bytes in Python?",
        "`str` represents Unicode text; `bytes` represents a sequence of byte values. Encode text at an external boundary with `text.encode('utf-8')`, and decode bytes with `data.decode('utf-8')`. Choose the correct encoding when reading files or network data.",
        ("str", "bytes", "string", "text", "unicode", "encode", "decode", "difference"), ("str vs bytes", "bytes versus string", "difference between str and bytes"),
    ),
    KnowledgeEntry(
        "How do I merge dictionaries in Python?",
        "On Python 3.9 and newer, `merged = first | second` creates a new dictionary; keys from `second` replace duplicate keys from `first`. Use `first.update(second)` to modify `first` in place. For older Python versions, `{**first, **second}` creates a merged dictionary.",
        ("merge", "dictionary", "dict", "combine", "update", "mapping", "union"), ("merge two dictionaries", "combine dictionaries", "dictionary merge"),
    ),
    KnowledgeEntry(
        "How do I use heapq as a priority queue?",
        "Python's `heapq` is a min-heap: push `(priority, item)` pairs with `heappush` and remove the smallest with `heappop`. Add a tie-break counter if items at equal priority are not comparable. To get the largest item first, negate numeric priorities.",
        ("heapq", "priority", "queue", "heap", "push", "pop", "minimum", "python"), ("heapq priority queue", "python priority queue", "use heapq", "priority queue with heapq"),
    ),
    KnowledgeEntry(
        "How do I traverse a binary tree level by level?",
        "Use breadth-first search with a `deque`: remove nodes from the front and enqueue their children. Each node is visited once, so the traversal takes O(n) time and O(w) space, where w is the maximum width of the tree. For level groups, process the queue's current length before moving to the next level.",
        ("binary", "tree", "level", "order", "traverse", "bfs", "breadth", "deque", "python"), ("level order traversal", "tree level by level", "breadth first traversal of a tree"),
    ),
    KnowledgeEntry(
        "How do I find the lowest common ancestor in a binary search tree?",
        "In a BST, compare both target values with the current node. If both are smaller, go left; if both are larger, go right; otherwise the current node is the split point and is their lowest common ancestor. This takes O(h) time for tree height h.",
        ("lowest", "common", "ancestor", "lca", "binary", "search", "tree", "bst", "node"), ("lowest common ancestor in a bst", "lowest common ancestor in a binary search tree", "find lca in binary search tree", "bst common ancestor"),
    ),
    KnowledgeEntry(
        "How do I implement merge sort in Python?",
        "Merge sort splits the input, sorts each half, and merges the sorted halves. It takes O(n log n) time and O(n) extra space, and is stable when equal items are taken from the left half first. Python's built-in `sorted()` is usually the better production choice.",
        ("merge", "sort", "sorting", "implement", "divide", "conquer", "stable", "python", "code"), ("merge sort implementation", "implement merge sort", "merge sort code"),
    ),
    KnowledgeEntry(
        "How do I find the kth largest value with quickselect?",
        "Quickselect partitions around a pivot and continues only in the partition containing the requested index. For the kth largest value in a list of length n, the ascending target index is `n - k`. Its average time is O(n), with O(n²) worst case; `heapq.nlargest(k, values)[-1]` is a convenient standard-library alternative.",
        ("quickselect", "kth", "largest", "select", "partition", "pivot", "order statistic"), ("quickselect kth largest", "kth largest quickselect", "kth largest value with quickselect", "select kth element"),
    ),
    KnowledgeEntry(
        "How do I reconstruct a shortest path found by BFS?",
        "During BFS, store `parent[neighbor] = current` the first time each vertex is visited. When the destination is reached, follow parent links backward to the start, then reverse that list. BFS gives a shortest path by number of edges in an unweighted graph; its traversal cost is O(V + E).",
        ("reconstruct", "shortest", "path", "bfs", "parent", "unweighted", "graph", "route"), ("reconstruct bfs path", "reconstruct a shortest path found by bfs", "reconstruct shortest path found by bfs", "get path from bfs", "shortest path reconstruction"),
    ),
    KnowledgeEntry(
        "How do I answer range-sum queries with prefix sums?",
        "Build a prefix array with a leading zero so `prefix[i]` stores the sum before index i. Then the inclusive sum from `left` to `right` is `prefix[right + 1] - prefix[left]`. Building takes O(n), and each query takes O(1); this works for negative values too.",
        ("range", "sum", "query", "prefix", "array", "subarray", "inclusive"), ("range sum query", "prefix sum range query", "sum a range efficiently"),
    ),
    KnowledgeEntry(
        "How do I use pathlib to work with file paths?",
        "Use `pathlib.Path` to build paths with `/`, inspect them, and read or write files. A `Path` represents a filesystem path without requiring manual separator handling. For example, `Path('data') / 'input.txt'` creates a child path; use `read_text()` or `write_text()` for small text files.",
        ("pathlib", "path", "file", "directory", "filesystem", "read_text", "write_text"), ("python pathlib", "work with file paths", "pathlib path"),
    ),
    KnowledgeEntry(
        "How do I format strings with f-strings?",
        "Prefix a string with `f` and put expressions in braces: `f'Hello, {name}!'`. Format numbers with a specifier such as `f'{price:.2f}'` for two decimal places. For literal braces, double them as `{{` and `}}`; avoid putting untrusted input into expressions evaluated by `eval`.",
        ("f-string", "fstrings", "format", "string", "interpolation", "brace", "python"), ("format string in python", "python f string", "string interpolation"),
    ),
    KnowledgeEntry(
        "How do I use a generator expression in Python?",
        "A generator expression uses parentheses, such as `(item * item for item in values)`, and computes values lazily as they are requested. It can save memory when passing a one-time stream to `sum`, `any`, or a loop. Use a list comprehension when you need to reuse or index the results.",
        ("generator", "expression", "lazy", "yield", "comprehension", "memory", "iterable"), ("generator expression", "lazy comprehension", "create a generator expression"),
    ),
    KnowledgeEntry(
        "How do I safely look up a dictionary key with a default?",
        "Use `mapping.get(key, default)` when a missing key should return a fallback instead of raising `KeyError`. Use `key in mapping` when you need to distinguish a missing key from a key whose value is `None`. For nested data, check each level or use a deliberate helper rather than assuming every key exists.",
        ("dictionary", "dict", "lookup", "key", "default", "get", "missing", "keyerror"), ("dict get default", "dictionary default value", "safe dictionary lookup"),
    ),
    KnowledgeEntry(
        "How do I search a rotated sorted array?",
        "Use modified binary search. At each step, one half is sorted; check whether the target lies inside that half's endpoints, then keep that half or discard it. This takes O(log n) time when values are distinct; duplicates can make some cases O(n).",
        ("rotated", "sorted", "array", "search", "binary", "target", "pivot"), ("search rotated sorted array", "rotated array search", "binary search rotated array"),
    ),
    KnowledgeEntry(
        "How do I find the longest increasing subsequence?",
        "For a strictly increasing subsequence in O(n log n), maintain `tails`, where each position stores the smallest possible ending value for a subsequence of that length. For each value, use `bisect_left` to replace the first tail greater than or equal to it. The length of `tails` is the answer; reconstructing the actual subsequence needs parent links too.",
        ("longest", "increasing", "subsequence", "lis", "bisect", "dynamic", "programming", "tails"), ("longest increasing subsequence", "lis algorithm", "find lis length"),
    ),
    KnowledgeEntry(
        "How do I find the minimum window substring?",
        "Use a sliding window and a character-count map. Expand the right edge until the window covers all required counts, then move the left edge right while coverage remains valid, recording the smallest valid range. With count maps this is O(n + m) time for source length n and target length m.",
        ("minimum", "window", "substring", "sliding", "string", "character", "count", "cover"), ("minimum window substring", "smallest substring containing characters", "min window string problem"),
    ),
    KnowledgeEntry(
        "How do I calculate edit distance between two strings?",
        "Levenshtein edit distance allows insertion, deletion, and substitution. A DP cell for prefixes `i` and `j` is the minimum of deleting, inserting, or substituting/matching the last character. The standard method takes O(mn) time; rolling rows reduce space to O(min(m, n)) when only the distance is needed.",
        ("edit", "distance", "levenshtein", "string", "insert", "delete", "substitute", "dynamic", "programming"), ("edit distance", "levenshtein distance", "minimum edits between strings"),
    ),
    KnowledgeEntry(
        "How do I merge k sorted lists efficiently?",
        "Put the first item from each non-empty list into a min-heap along with its list and index. Repeatedly remove the smallest item, append it, and push the next item from that same list. This takes O(N log k) time for N total items and O(k) heap space.",
        ("merge", "sorted", "lists", "k-way", "heap", "heapq", "priority", "array"), ("merge k sorted lists", "merge multiple sorted arrays", "k way merge"),
    ),
    KnowledgeEntry(
        "How do I use bisect to search a sorted list?",
        "The `bisect` module finds insertion positions in a sorted sequence in O(log n) time. `bisect_left(values, x)` returns the first position where x can go without breaking order; `bisect_right` returns the position after existing equal values. Inserting into a Python list still costs O(n) because later elements shift.",
        ("bisect", "binary", "search", "sorted", "insertion", "position", "bisect_left", "bisect_right"), ("python bisect module", "bisect to search a sorted list", "find insertion point in sorted list", "bisect sorted list"),
    ),
    KnowledgeEntry(
        "How do I count items with collections.Counter?",
        "`collections.Counter` counts hashable values and behaves like a dictionary from item to count: `Counter(words)`. Use `counter.most_common(k)` for the k most frequent items, and `counter[item]` returns zero for an unseen item. For unhashable values, convert them to a hashable key first.",
        ("counter", "collections", "count", "frequency", "most_common", "hashable", "items"), ("python counter", "count item frequencies", "collections counter"),
    ),
    KnowledgeEntry(
        "How do I group values with defaultdict?",
        "`collections.defaultdict(list)` creates a new list the first time a key is accessed, which makes grouping concise:\n\n```python\nfrom collections import defaultdict\n\ngroups = defaultdict(list)\nfor item in items:\n    groups[item.category].append(item)\n```\nUse `defaultdict(set)` when duplicates should be removed, or a normal dictionary if missing-key access should remain an error.",
        ("defaultdict", "group", "grouping", "collections", "list", "dictionary", "dict"), ("group values in python", "defaultdict grouping", "group items by key"),
    ),
    KnowledgeEntry(
        "How do I sort a list of dictionaries by a field?",
        "Pass a `key` function to `sorted` or `list.sort`. For example, `sorted(records, key=lambda row: row['age'])` sorts by age; add `reverse=True` for descending order. Python's sort is stable, so equal-key items keep their original relative order.",
        ("sort", "list", "dictionary", "dict", "field", "key", "records", "lambda"), ("sort a list of dictionaries", "sort dictionaries by key", "sort list of dicts", "sort records by field"),
    ),
    KnowledgeEntry(
        "How does match-case work in Python?",
        "`match` compares a value against `case` patterns and runs the first matching block. It supports literals, sequences, mappings, class patterns, and a fallback `case _:`. Structural pattern matching was added in Python 3.10; use ordinary `if` statements when they make simple conditions clearer.",
        ("match", "case", "pattern", "structural", "matching", "switch", "python"), ("match case statement", "match case work in python", "python pattern matching", "structural pattern matching"),
    ),
    KnowledgeEntry(
        "What does the walrus operator do in Python?",
        "The assignment expression `:=` assigns a value as part of a larger expression. For example, `while (line := file.readline()):` reads and tests each line in one condition. Use it sparingly: a separate assignment is often easier to read, and the operator does not replace normal `=` statements.",
        ("walrus", "operator", "assignment", "expression", "colon", "equals", "python"), ("walrus operator", "assignment expression", "colon equals operator"),
    ),
    KnowledgeEntry(
        "How do I check whether a path exists with pathlib?",
        "Create a `Path` and call `exists()` to check whether anything is at that path, `is_file()` for a regular file, or `is_dir()` for a directory. The filesystem can change after the check, so still handle `FileNotFoundError` or other `OSError` exceptions when opening or modifying the path.",
        ("pathlib", "path", "exists", "file", "directory", "is_file", "is_dir", "filesystem"), ("check if file exists python", "path exists pathlib", "check path exists"),
    ),
    KnowledgeEntry(
        "What are common Python collection operation costs?",
        "Typical costs: list indexing is O(1), append is O(1) amortized, and inserting/removing at the front is O(n). Dict and set lookup are O(1) average. `deque` append/pop at either end are O(1). A heap peek is O(1), while push/pop are O(log n). Exact costs depend on the operation and implementation.",
        ("collection", "operation", "complexity", "cost", "list", "append", "dict", "set", "deque", "heap"), ("python data structure time complexity", "complexities of python collections", "list dict set complexity", "time complexity of list append", "time complexity of python list append", "list append complexity"),
    ),
    KnowledgeEntry(
        "How do I implement BFS in Python?",
        "Use `collections.deque` as a FIFO worklist and mark nodes visited when enqueuing them so each is added once. With an adjacency list, BFS takes O(V + E):\n\n```python\nfrom collections import deque\n\ndef bfs(graph, start):\n    seen = {start}\n    queue = deque([start])\n    order = []\n    while queue:\n        node = queue.popleft()\n        order.append(node)\n        for neighbor in graph.get(node, []):\n            if neighbor not in seen:\n                seen.add(neighbor)\n                queue.append(neighbor)\n    return order\n```",
        ("bfs", "breadth", "first", "search", "code", "python", "queue", "deque"), ("bfs implementation", "breadth first search code", "write bfs in python", "implement bfs in python"),
    ),
    KnowledgeEntry(
        "How do I implement DFS in Python?",
        "An explicit list can serve as a stack and avoids recursion-depth limits on deep graphs. Mark a node visited when removing it, and skip it if already seen. With an adjacency list this takes O(V + E):\n\n```python\ndef dfs(graph, start):\n    seen = set()\n    stack = [start]\n    order = []\n    while stack:\n        node = stack.pop()\n        if node in seen:\n            continue\n        seen.add(node)\n        order.append(node)\n        stack.extend(reversed(graph.get(node, [])))\n    return order\n```",
        ("dfs", "depth", "first", "search", "code", "python", "stack"), ("dfs implementation", "depth first search code", "write dfs in python", "implement dfs in python"),
    ),
    KnowledgeEntry(
        "How do I find connected components in a graph?",
        "For an undirected graph, start a BFS or DFS from each unvisited vertex. Each traversal discovers one connected component; label its visited vertices before starting the next traversal. An adjacency-list implementation takes O(V + E) time.",
        ("connected", "component", "graph", "bfs", "dfs", "visited", "undirected"), ("connected components", "find components in a graph"),
    ),
    KnowledgeEntry(
        "How do I detect a cycle in a directed graph?",
        "Use depth-first search with three states: unseen, currently on the recursion path, and fully processed. An edge to a node currently on the path is a back edge and proves a cycle. This takes O(V + E); for very deep graphs, use an iterative DFS to avoid recursion limits.",
        ("cycle", "detect", "directed", "graph", "dfs", "back", "edge"), ("directed graph cycle", "cycle in a directed graph", "detect directed cycle"),
    ),
    KnowledgeEntry(
        "How do I check whether a graph is bipartite?",
        "Try coloring each vertex with one of two colors so every edge connects different colors. BFS or DFS propagates the opposite color to each neighbor; a conflict means the graph is not bipartite. Start a traversal in every component. This takes O(V + E).",
        ("bipartite", "graph", "color", "colour", "bfs", "dfs", "odd", "cycle"), ("bipartite graph", "check if a graph is bipartite", "two-color a graph"),
    ),
    KnowledgeEntry(
        "What is the longest common subsequence problem?",
        "A subsequence keeps the original order but may skip items. For strings A and B, dynamic programming compares prefixes: matching characters add one to the diagonal result; otherwise take the larger of the top or left result. The standard table uses O(mn) time and space; rolling rows can reduce space when only the length is needed.",
        ("longest", "common", "subsequence", "lcs", "dynamic", "programming", "string"), ("longest common subsequence", "lcs problem"),
    ),
    KnowledgeEntry(
        "How does the 0/1 knapsack dynamic program work?",
        "For each item, choose whether to take it without exceeding capacity. With a one-dimensional DP array, iterate capacities downward so an item cannot be reused in the same pass. This takes O(nC) time and O(C) space for n items and capacity C; it is pseudo-polynomial because it depends on the numeric capacity.",
        ("knapsack", "zero", "one", "01", "dynamic", "programming", "capacity", "weight", "value"), ("0/1 knapsack", "zero one knapsack", "knapsack dynamic programming"),
    ),
    KnowledgeEntry(
        "What is the difference between memoization and tabulation?",
        "Memoization is top-down: a recursive function caches answers when needed. Tabulation is bottom-up: a loop fills a table in dependency order. Both reuse subproblem results; choose the one with clearer state transitions, and consider recursion depth and memory use.",
        ("memoization", "tabulation", "top", "down", "bottom", "up", "dynamic", "programming", "cache"), ("memoization vs tabulation", "top-down vs bottom-up dp", "difference between memoization and tabulation"),
    ),
    KnowledgeEntry(
        "How do I find the maximum-sum subarray?",
        "Kadane's algorithm tracks the best subarray ending at the current position and the best seen overall. At each value, either extend the prior subarray or start fresh. It runs in O(n) time and O(1) extra space; initialize from the first value so all-negative inputs work.",
        ("maximum", "maximum-sum", "subarray", "sum", "kadane", "array"), ("maximum subarray", "max subarray sum", "kadane algorithm"),
    ),
    KnowledgeEntry(
        "How do I find the next greater element?",
        "Scan left to right with a monotonic decreasing stack of indices. When a new value is larger than the value at the stack top, it is the next greater element for that index; pop and record it. Each index is pushed and popped once, so the algorithm is O(n).",
        ("next", "greater", "element", "monotonic", "stack", "array"), ("next greater element", "next greater number"),
    ),
    KnowledgeEntry(
        "How does greedy interval scheduling work?",
        "To select the largest number of non-overlapping intervals, sort by end time and repeatedly choose the next interval whose start is at or after the last chosen end. This greedy rule is optimal for this specific objective and takes O(n log n) time because of sorting. Greedy choices need a proof for each problem.",
        ("greedy", "interval", "schedule", "non-overlap", "end", "activity", "selection"), ("interval scheduling", "activity selection", "maximum non-overlapping intervals"),
    ),
    KnowledgeEntry(
        "How do I find the maximum in every sliding window?",
        "Use a decreasing deque of indices. Remove indices that have left the window from the front, and remove smaller values from the back because they cannot be a future maximum. The front is the current maximum. Each index is added and removed once, giving O(n) time.",
        ("sliding", "window", "maximum", "max", "deque", "monotonic", "queue"), ("sliding window maximum", "maximum of each window", "max in every window", "maximum in every sliding window"),
    ),
    KnowledgeEntry(
        "How do I write Fibonacci with memoization?",
        "Memoization caches each Fibonacci result so the recursive definition does not recompute the same values exponentially many times. Python's `functools.cache` is available in Python 3.9 and newer:\n\n```python\nfrom functools import cache\n\n@cache\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n```\nFor very large n, an iterative solution avoids recursion-depth limits.",
        ("fibonacci", "fib", "memoization", "cache", "recursion", "dynamic"), ("fibonacci memoization", "memoized fibonacci", "fibonacci with cache"),
    ),
    KnowledgeEntry(
        "Why should I avoid mutable default arguments?",
        "Default argument values are created once when the function is defined, so a mutable default such as `items=[]` is shared across calls. Use `None` and create a new list inside the function instead: `def add(value, items=None):\n    if items is None:\n        items = []\n    items.append(value)\n    return items`.",
        ("mutable", "default", "argument", "list", "shared", "function"), ("mutable default argument", "default list argument", "empty list default parameter"),
    ),
    KnowledgeEntry(
        "What is the difference between is and == in Python?",
        "`==` compares values for equality. `is` checks whether two references point to the same object. Use `is None` for the singleton `None`; do not use `is` to compare ordinary strings or numbers.",
        ("is", "==", "difference", "identity", "equality", "equal", "same", "object", "none"), ("is vs equals", "is versus ==", "identity vs equality", "difference between is and equals"),
    ),
)

KNOWLEDGE_BASE += tuple(
    KnowledgeEntry(
        question,
        answer,
        tuple(re.findall(r"[a-z0-9_]+", question.lower())),
    )
    for question, answer in ADDITIONAL_KNOWLEDGE
)
KNOWLEDGE_BASE += tuple(
    KnowledgeEntry(
        question,
        answer,
        tuple(re.findall(r"[a-z0-9_]+", question.lower())),
    )
    for question, answer in API_KNOWLEDGE
)

# Add natural-language forms for 100 frequently useful Python and DSA answers.
# These entries reuse curated answers; they improve retrieval for everyday
# phrasing without fabricating or paraphrasing technical facts.
_COMMON_TERMS = {
    "python", "string", "list", "tuple", "dict", "dictionary", "set", "function", "loop",
    "variable", "type", "class", "object", "file", "module", "package", "exception", "error",
    "queue", "stack", "array", "sort", "search", "algorithm", "complexity",
    "recursion", "cache", "hash", "iterator", "generator", "async", "test", "debug",
    "copy", "range", "condition", "import", "path", "json", "csv", "regex", "date", "time",
    "number", "integer",
    "float", "boolean", "mutable", "immutable", "comprehension", "decorator", "context", "thread",
    "process", "database", "http", "api", "pip", "venv", "memory", "performance", "typing", "pep",
}
_COMMON_VERBS = ("implement", "create", "define", "write", "use", "make", "find", "calculate", "check", "sort", "search", "traverse", "build", "handle", "work with", "approach", "reason about", "detect", "merge", "evaluate")
_COMMON_PREFIXES = ("What is ", "What are ", "What does ", "What do ", "How do I ", "How do ", "How does ", "How can I ", "How can ", "Why does ", "Why can ", "When should I ", "When should ", "Is ", "Can I ", "Can ")

def _common_topic(question: str) -> str:
    topic = question.rstrip("?.!")
    for prefix in _COMMON_PREFIXES:
        if topic.lower().startswith(prefix.lower()):
            topic = topic[len(prefix):]
            break
    topic = re.sub(r"\b(?:in|with|using) Python$", "", topic, flags=re.IGNORECASE).strip()
    for verb in _COMMON_VERBS:
        if topic.lower().startswith(verb + " "):
            topic = topic[len(verb):].strip()
            break
    if topic.lower().startswith("python "):
        topic = topic[len("python "):].strip()
    topic = re.sub(r"^work with\s+", "", topic, flags=re.IGNORECASE).strip()
    return topic[:1].lower() + topic[1:] if topic else question.rstrip("?.!")

_common_candidates = []
for _entry in KNOWLEDGE_BASE:
    _question_words = set(re.findall(r"[a-z0-9_]+", _entry.question.lower()))
    if (
        _entry.question.startswith("What does ")
        or _entry.question.startswith("What is Python commonly used")
        or _entry.question.startswith("How can a stack evaluate")
        or not (_question_words & _COMMON_TERMS)
    ):
        continue
    _common_candidates.append((len(_question_words & _COMMON_TERMS), _entry))
_common_sources = []
_common_source_topics = set()
for _, _entry in sorted(_common_candidates, key=lambda item: (-item[0], item[1].question)):
    _topic = _common_topic(_entry.question).lower()
    if _topic in _common_source_topics:
        continue
    _common_sources.append(_entry)
    _common_source_topics.add(_topic)
    if len(_common_sources) == 100:
        break
_common_templates = (
    "Could you explain {topic} in Python?",
    "Give me a simple explanation of {topic}.",
    "What should I know about {topic} in Python?",
    "Can you summarize {topic} for me?",
    "I am new to Python; how does {topic} work?",
)
_common_variants = tuple(
    KnowledgeEntry(
        template.format(topic=_common_topic(source.question)),
        source.answer,
        tuple(set(source.keywords) | set(re.findall(r"[a-z0-9_]+", source.question.lower()))),
        ("python " + _common_topic(source.question),),
        True,
    )
    for source in _common_sources
    for template in _common_templates
)
KNOWLEDGE_BASE += _common_variants
if len(_common_sources) != 100 or len(_common_variants) != 500:
    raise RuntimeError(f"Expected 500 common question variants, found {len(_common_variants)}")
if len(KNOWLEDGE_BASE) != 2506:
    raise RuntimeError(f"Expected 2506 knowledge entries, found {len(KNOWLEDGE_BASE)}")

VISUALS_BY_QUESTION = {
    "How do I search a rotated sorted array?": "binary-search",
    "How do I find the longest increasing subsequence?": "lis",
    "How do I find the minimum window substring?": "sliding-window",
    "How do I calculate edit distance between two strings?": "edit-distance",
    "How do I merge k sorted lists efficiently?": "heap",
    "How do I use bisect to search a sorted list?": "binary-search",
    "How do I use heapq as a priority queue?": "heap",
    "How do I traverse a binary tree level by level?": "tree-traversal",
    "How do I find the lowest common ancestor in a binary search tree?": "bst",
    "How do I implement merge sort in Python?": "sorting",
    "How do I find the kth largest value with quickselect?": "sorting",
    "How do I reconstruct a shortest path found by BFS?": "graph-search",
    "How do I answer range-sum queries with prefix sums?": "prefix-sum",
    "How do I create a trie in Python?": "trie",
    "How do I implement an LRU cache in Python?": "hash-table",
    "How do I calculate the height of a binary tree?": "tree",
    "How do I detect a cycle in an undirected graph?": "graph",
    "How do I sum every fixed-size sliding window?": "sliding-window",
    "How do I count paths through a grid with obstacles?": "dynamic-programming",
    "How do I implement binary search in Python?": "binary-search",
    "How do I implement Dijkstra's algorithm in Python?": "dijkstra",
    "How do I implement topological sorting in Python?": "topological",
    "How do I implement union-find in Python?": "union-find",
    "How do I generate all subsets with backtracking?": "backtracking",
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
    "What is a binary tree?": "tree",
    "What is a binary search tree?": "bst",
    "What is a heap?": "heap",
    "How do I make a priority queue?": "heap",
    "What is a graph data structure?": "graph",
    "What is the difference between an adjacency list and matrix?": "graph",
    "What are BFS and DFS?": "graph-search",
    "How do I find a shortest path in an unweighted graph?": "graph-search",
    "How do I choose a shortest-path algorithm?": "graph",
    "What are common Python collection operation costs?": "complexity",
    "How do I implement BFS in Python?": "graph-search",
    "How do I implement DFS in Python?": "graph-search",
    "How do I find connected components in a graph?": "graph",
    "How do I detect a cycle in a directed graph?": "graph",
    "How do I check whether a graph is bipartite?": "graph",
    "What is the longest common subsequence problem?": "dynamic-programming",
    "How does the 0/1 knapsack dynamic program work?": "dynamic-programming",
    "What is the difference between memoization and tabulation?": "dynamic-programming",
    "How do I find the maximum-sum subarray?": "array",
    "How do I find the next greater element?": "monotonic",
    "How does greedy interval scheduling work?": "sorting",
    "How do I find the maximum in every sliding window?": "monotonic",
    "How do I write Fibonacci with memoization?": "recursion",
    "How do I solve the Two Sum problem?": "two-sum",
    "How do prefix sums work?": "prefix-sum",
    "How do I merge overlapping intervals?": "sorting",
    "How do I find the kth largest value?": "heap",
    "How can I detect a cycle in a linked list?": "linked-list",
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
    "What is complexity analysis?": "complexity",
    "What is time complexity?": "complexity",
    "What is space complexity?": "complexity",
    "What are the two-pointer and sliding-window techniques?": "sliding-window",
    "What is dynamic programming?": "dynamic-programming",
    "What is backtracking?": "backtracking",
    "What is branch and bound?": "backtracking",
    "What is A* search?": "graph-search",
    "What is Kruskal's algorithm?": "graph-search",
    "How do I sort a dictionary in Python?": "sorting",
    "What is the difference between a list and a tuple?": "array",
    "What is a trie?": "trie",
    "What are segment trees and Fenwick trees?": "range-trees",
    "What is disjoint set union (union-find)?": "union-find",
    "What is a monotonic stack or queue?": "monotonic",
    "What is topological sorting?": "topological",
    "What is Dijkstra's algorithm?": "dijkstra",
    "What is the Bellman-Ford algorithm?": "graph",
    "What is the Floyd-Warshall algorithm?": "graph",
    "What is counting sort or radix sort?": "sorting",
    "What is a Bloom filter?": "bloom-filter",
    "How do I check whether two strings are anagrams?": "anagram",
    "How do I check balanced parentheses?": "parentheses",
    "How do I find the shortest word ladder?": "word-ladder",
    "What is recursion?": "recursion",
}

STOP_WORDS = {"a", "an", "and", "are", "can", "data", "do", "doe", "does", "for", "how", "i", "in", "is", "it", "of", "python", "runtime", "s", "structure", "to", "what", "with", "algorithm", "you", "your", "about", "beginner", "explain", "help", "know", "me", "please", "simple", "should", "summarize", "understand", "quick"}
GENERIC_MATCH_WORDS = {"complexity", "function", "operation", "runtime", "search", "space", "time", "value"}


def normalize(text: str) -> list[str]:
    """Return lowercase words with common English plurals reduced to their base form."""
    text = re.sub(r"\ba\s*\*", "a star", text.lower()).replace("==", " equals ")
    words = re.findall(r"[a-z0-9_]+", text)
    normalized = []
    for word in words:
        word = word.strip("_") or word
        if word in {"args", "kwargs", "itertools", "functools"}:
            pass  # These words end in s but are not ordinary English plurals.
        elif word == "tries":
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
    normalized_question = " ".join(normalize(question))
    exact_title = next(
        (entry for entry in KNOWLEDGE_BASE if " ".join(normalize(entry.question)) == normalized_question),
        None,
    )
    if exact_title:
        return exact_title
    if re.search(r"\bmap\s*\(", question, re.IGNORECASE):
        return next(entry for entry in KNOWLEDGE_BASE if entry.question == "What does Python's map() function do?")
    words = set(normalize(question)) - STOP_WORDS
    if not words:
        if "python" in normalize(question):
            return next(entry for entry in KNOWLEDGE_BASE if entry.question == "What is Python?")
        return None

    question_tokens = normalize(question)
    question_normalized = " ".join(question_tokens)
    best_entry: KnowledgeEntry | None = None
    best_score = 0.0

    for entry in KNOWLEDGE_BASE:
        if entry.exact_only:
            continue
        # Normalize knowledge-base terms too, so plural forms match singular
        # keywords while technical names remain searchable.
        keywords = {word for keyword in entry.keywords for word in normalize(keyword)}
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
        alias_hit = False
        for phrase in entry.aliases:
            phrase_tokens = normalize(phrase)
            phrase_words = " ".join(phrase_tokens)
            # Multi-word aliases may occur within a natural-language question.
            # A one-word alias should only boost a topic-only prompt; otherwise
            # generic terms such as "string" can hijack a specific question.
            alias_matches = (
                bool(phrase_tokens)
                and (
                    (len(phrase_tokens) == 1 and words == set(phrase_tokens))
                    or (len(phrase_tokens) > 1 and phrase_words in question_normalized)
                )
            )
            if alias_matches:
                alias_hit = True
        if alias_hit:
            score += 1.0
        # One broad word should not turn a question with several unrelated
        # terms into a confident but misleading answer. Exact phrase aliases
        # still allow concise questions such as "time complexity".
        if len(words) > 2 and len(exact_overlap) == 1 and exact_overlap <= GENERIC_MATCH_WORDS and not alias_hit:
            continue
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
