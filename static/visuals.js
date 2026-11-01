(() => {
  const diagrams = {
    workflow: {
      title: 'A practical problem-solving loop',
      alt: 'Seven steps: understand, examples, simple solution, choose tools, prove and analyze, implement, test.',
      svg: '<g class="viz-flow"><rect x="10" y="42" width="88" height="44" rx="10"/><text x="54" y="60">Understand</text><text x="54" y="74">the task</text><path d="M100 64h15"/><rect x="118" y="42" width="78" height="44" rx="10"/><text x="157" y="60">Try small</text><text x="157" y="74">examples</text><path d="M198 64h15"/><rect x="216" y="42" width="78" height="44" rx="10"/><text x="255" y="60">Start with</text><text x="255" y="74">a simple idea</text><path d="M296 64h15"/><rect x="314" y="42" width="78" height="44" rx="10"/><text x="353" y="60">Choose data</text><text x="353" y="74">and algorithm</text></g><g class="viz-note"><text x="20" y="123">Then prove it, analyze cost, implement, and test edge cases.</text></g>'
    },
    array: {
      title: 'Array / Python list', alt: 'Indexed array cells with constant-time access by index.',
      svg: '<g class="viz-index"><text x="45" y="40">0</text><text x="115" y="40">1</text><text x="185" y="40">2</text><text x="255" y="40">3</text><text x="325" y="40">4</text></g><g class="viz-cells"><rect x="15" y="50" width="60" height="48" rx="8"/><rect x="85" y="50" width="60" height="48" rx="8"/><rect x="155" y="50" width="60" height="48" rx="8"/><rect x="225" y="50" width="60" height="48" rx="8"/><rect x="295" y="50" width="60" height="48" rx="8"/></g><g class="viz-values"><text x="45" y="80">4</text><text x="115" y="80">8</text><text x="185" y="80">15</text><text x="255" y="80">16</text><text x="325" y="80">23</text></g><text class="viz-note" x="185" y="128">index → value</text>'
    },
    stack: {
      title: 'Stack · last in, first out', alt: 'Stack with top item removed first and new items pushed onto the top.',
      svg: '<text class="viz-note" x="73" y="34">push →</text><rect class="viz-highlight" x="112" y="20" width="100" height="31" rx="7"/><rect class="viz-cells" x="112" y="55" width="100" height="31" rx="7"/><rect class="viz-cells" x="112" y="90" width="100" height="31" rx="7"/><text class="viz-values" x="162" y="41">new · C</text><text class="viz-values" x="162" y="76">B</text><text class="viz-values" x="162" y="111">A</text><path class="viz-accent-stroke" d="M260 36h55m-9-8 9 8-9 8"/><text class="viz-note" x="316" y="40">pop</text><text class="viz-note" x="162" y="145">TOP</text>'
    },
    queue: {
      title: 'Queue · first in, first out', alt: 'Queue: add items at the rear, remove the oldest item at the front.',
      svg: '<text class="viz-note" x="48" y="34">FRONT · dequeue</text><text class="viz-note" x="298" y="34">enqueue · REAR</text><g class="viz-cells"><rect x="35" y="52" width="68" height="44" rx="8"/><rect x="107" y="52" width="68" height="44" rx="8"/><rect x="179" y="52" width="68" height="44" rx="8"/><rect x="251" y="52" width="68" height="44" rx="8"/></g><g class="viz-values"><text x="69" y="79">oldest</text><text x="141" y="79">next</text><text x="213" y="79">…</text><text x="285" y="79">newest</text></g><path class="viz-accent-stroke" d="M15 74h16m-6-6 6 6-6 6M338 74h25m-7-6 7 6-7 6"/><text class="viz-note" x="190" y="127">deque: append() + popleft()</text>'
    },
    'circular-queue': {
      title: 'Circular queue · fixed-capacity buffer', alt: 'Circular queue cells wrap from the last slot back to the first.',
      svg: '<path class="viz-link" d="M102 30C132 4 253 4 284 30M285 109C251 135 134 135 100 109"/><path class="viz-accent-stroke" d="M275 25l10 5-11 4M108 103l-10 6 11 4"/><g class="viz-cells"><rect x="35" y="48" width="62" height="43" rx="9"/><rect x="103" y="48" width="62" height="43" rx="9"/><rect x="171" y="48" width="62" height="43" rx="9"/><rect x="239" y="48" width="62" height="43" rx="9"/></g><g class="viz-values"><text x="66" y="74">A</text><text x="134" y="74">B</text><text x="202" y="74">C</text><text x="270" y="74">empty</text></g><text class="viz-note" x="168" y="123">tail wraps to index 0</text>'
    },
    'linked-list': {
      title: 'Singly linked list', alt: 'Nodes store a value and a reference to the next node.',
      svg: '<text class="viz-note" x="45" y="40">head</text><path class="viz-accent-stroke" d="M47 43v9"/><g class="viz-cells"><rect x="18" y="55" width="94" height="48" rx="8"/><rect x="148" y="55" width="94" height="48" rx="8"/><rect x="278" y="55" width="94" height="48" rx="8"/></g><path class="viz-link" d="M112 79h29m-7-6 7 6-7 6M242 79h29m-7-6 7 6-7 6"/><g class="viz-values"><text x="65" y="84">value · next</text><text x="195" y="84">value · next</text><text x="325" y="84">value · None</text></g><text class="viz-note" x="195" y="130">follow references node by node</text>'
    },
    'hash-table': {
      title: 'Hash table / Python dict', alt: 'Keys pass through a hash function and point to buckets containing values.',
      svg: '<rect class="viz-cells" x="20" y="37" width="104" height="42" rx="8"/><text class="viz-values" x="72" y="63">"Ada"</text><path class="viz-link" d="M124 58h50m-8-6 8 6-8 6"/><rect class="viz-highlight" x="180" y="37" width="94" height="42" rx="8"/><text class="viz-values" x="227" y="63">hash(key)</text><path class="viz-link" d="M274 58h41m-8-6 8 6-8 6"/><rect class="viz-cells" x="322" y="37" width="66" height="42" rx="8"/><text class="viz-values" x="355" y="63">36</text><text class="viz-note" x="72" y="103">key</text><text class="viz-note" x="227" y="103">hash</text><text class="viz-note" x="355" y="103">value</text><text class="viz-note" x="204" y="134">average lookup: O(1)</text>'
    },
    tree: {
      title: 'Tree structure', alt: 'Root node branches to child nodes in a hierarchy.',
      svg: '<path class="viz-link" d="M195 38L112 79M195 38L278 79M112 96L68 125M112 96L156 125"/><g class="viz-node"><circle cx="195" cy="30" r="19"/><circle cx="112" cy="83" r="19"/><circle cx="278" cy="83" r="19"/><circle cx="68" cy="130" r="17"/><circle cx="156" cy="130" r="17"/></g><g class="viz-values"><text x="195" y="34">root</text><text x="112" y="87">child</text><text x="278" y="87">child</text><text x="68" y="134">leaf</text><text x="156" y="134">leaf</text></g>'
    },
    bst: {
      title: 'Binary search tree', alt: 'Balanced binary search tree: smaller values left, larger values right.',
      svg: '<path class="viz-link" d="M195 36L112 82M195 36L278 82M112 99L68 129M112 99L156 129M278 99L244 129M278 99L318 129"/><g class="viz-node"><circle cx="195" cy="30" r="20"/><circle cx="112" cy="88" r="20"/><circle cx="278" cy="88" r="20"/><circle cx="68" cy="133" r="17"/><circle cx="156" cy="133" r="17"/><circle cx="244" cy="133" r="17"/><circle cx="318" cy="133" r="17"/></g><g class="viz-values"><text x="195" y="34">8</text><text x="112" y="92">4</text><text x="278" y="92">12</text><text x="68" y="137">2</text><text x="156" y="137">6</text><text x="244" y="137">10</text><text x="318" y="137">14</text></g>'
    },
    heap: {
      title: 'Min-heap', alt: 'A min-heap keeps the smallest value at the root; the heap array stores it level by level.',
      svg: '<path class="viz-link" d="M104 52L62 91M104 52L146 91M62 109L42 132M62 109L82 132"/><g class="viz-node"><circle cx="104" cy="46" r="18"/><circle cx="62" cy="97" r="17"/><circle cx="146" cy="97" r="17"/><circle cx="42" cy="137" r="15"/><circle cx="82" cy="137" r="15"/></g><g class="viz-values"><text x="104" y="50">1</text><text x="62" y="101">4</text><text x="146" y="101">3</text><text x="42" y="141">9</text><text x="82" y="141">7</text></g><text class="viz-note" x="260" y="53">heap order</text><rect class="viz-highlight" x="226" y="67" width="152" height="42" rx="8"/><text class="viz-values" x="302" y="93">[1, 4, 3, 9, 7]</text><text class="viz-note" x="302" y="130">level-order array</text>'
    },
    graph: {
      title: 'Graph · vertices and edges', alt: 'An undirected graph with four vertices and connecting edges.',
      svg: '<path class="viz-link" d="M76 60L178 38M76 60L112 122M178 38L286 69M178 38L212 126M112 122L212 126M212 126L286 69"/><g class="viz-node"><circle cx="76" cy="60" r="22"/><circle cx="178" cy="38" r="22"/><circle cx="286" cy="69" r="22"/><circle cx="112" cy="122" r="22"/><circle cx="212" cy="126" r="22"/></g><g class="viz-values"><text x="76" y="64">A</text><text x="178" y="42">B</text><text x="286" y="73">C</text><text x="112" y="126">D</text><text x="212" y="130">E</text></g><text class="viz-note" x="195" y="160">adjacency list: A → [B, D]</text>'
    },
    'graph-search': {
      title: 'Graph traversal', alt: 'Graph nodes labeled in breadth-first visit order from the start node.',
      svg: '<path class="viz-link" d="M72 77L177 44M72 77L126 132M177 44L290 77M177 44L230 132M126 132L230 132M230 132L290 77"/><g class="viz-node viz-node-visited"><circle cx="72" cy="77" r="23"/><circle cx="177" cy="44" r="23"/><circle cx="126" cy="132" r="23"/><circle cx="290" cy="77" r="23"/><circle cx="230" cy="132" r="23"/></g><g class="viz-values"><text x="72" y="81">1</text><text x="177" y="48">2</text><text x="126" y="136">3</text><text x="290" y="81">4</text><text x="230" y="136">5</text></g><text class="viz-note" x="194" y="166">BFS uses a queue · DFS uses a stack</text>'
    },
    'tree-traversal': {
      title: 'Tree traversal orders', alt: 'A tree with root 2, left child 1, and right child 3; inorder visits 1, 2, 3.',
      svg: '<path class="viz-link" d="M200 48L116 102M200 48L284 102"/><g class="viz-node"><circle cx="200" cy="43" r="22"/><circle cx="116" cy="108" r="22"/><circle cx="284" cy="108" r="22"/></g><g class="viz-values"><text x="200" y="47">2</text><text x="116" y="112">1</text><text x="284" y="112">3</text></g><text class="viz-note" x="200" y="155">inorder: 1 → 2 → 3</text>'
    },
    'binary-search': {
      title: 'Binary search', alt: 'Sorted values; binary search checks the middle value and discards half the range each step.',
      svg: '<g class="viz-index"><text x="40" y="41">0</text><text x="108" y="41">1</text><text x="176" y="41">2</text><text x="244" y="41">3</text><text x="312" y="41">4</text></g><g class="viz-cells"><rect x="12" y="50" width="56" height="44" rx="7"/><rect x="80" y="50" width="56" height="44" rx="7"/><rect x="148" y="50" width="56" height="44" rx="7"/><rect class="viz-highlight" x="216" y="50" width="56" height="44" rx="7"/><rect x="284" y="50" width="56" height="44" rx="7"/></g><g class="viz-values"><text x="40" y="78">3</text><text x="108" y="78">7</text><text x="176" y="78">11</text><text x="244" y="78">16</text><text x="312" y="78">21</text></g><path class="viz-accent-stroke" d="M244 101v17m-6-7 6 7 6-7"/><text class="viz-note" x="244" y="139">middle → discard half</text>'
    },
    search: {
      title: 'Choose a search strategy', alt: 'Linear scan checks items one by one; binary search halves a sorted list.',
      svg: '<text class="viz-label" x="85" y="34">Linear scan · O(n)</text><g class="viz-cells"><rect x="20" y="46" width="42" height="34" rx="6"/><rect class="viz-highlight" x="67" y="46" width="42" height="34" rx="6"/><rect x="114" y="46" width="42" height="34" rx="6"/><rect x="161" y="46" width="42" height="34" rx="6"/></g><text class="viz-note" x="270" y="67">check each item</text><text class="viz-label" x="85" y="111">Binary search · O(log n)</text><path class="viz-link" d="M21 132h182M112 119v24M65 119v24M158 119v24"/><circle class="viz-node" cx="112" cy="132" r="12"/><text class="viz-note" x="270" y="136">sorted data only</text>'
    },
    sorting: {
      title: 'Sorting values', alt: 'Bar chart of values before sorting and in ascending order after sorting.',
      svg: '<text class="viz-label" x="86" y="30">Before</text><text class="viz-label" x="282" y="30">After</text><g class="viz-bars"><rect x="38" y="70" width="24" height="64" rx="4"/><rect x="69" y="104" width="24" height="30" rx="4"/><rect x="100" y="49" width="24" height="85" rx="4"/><rect x="131" y="86" width="24" height="48" rx="4"/><rect x="228" y="104" width="24" height="30" rx="4"/><rect x="259" y="86" width="24" height="48" rx="4"/><rect x="290" y="70" width="24" height="64" rx="4"/><rect x="321" y="49" width="24" height="85" rx="4"/></g><path class="viz-accent-stroke" d="M170 90h39m-8-7 8 7-8 7"/><text class="viz-note" x="195" y="153">sorted(values) returns a new list</text>'
    },
    complexity: {
      title: 'Growth rates · input size n', alt: 'Line chart comparing constant, logarithmic, linear, n log n, and quadratic growth.',
      svg: '<path class="viz-axis" d="M42 18v118h326M42 136l6-8m-6 8 8 2M368 136l-8-5m8 5-8 5"/><text class="viz-note" x="19" y="26">cost</text><text class="viz-note" x="366" y="156">n</text><path class="viz-line viz-line-one" d="M48 122L356 120"/><path class="viz-line viz-line-log" d="M48 124Q115 97 180 91T356 81"/><path class="viz-line viz-line-linear" d="M48 130L356 58"/><path class="viz-line viz-line-nlog" d="M48 132Q170 130 225 105T356 35"/><path class="viz-line viz-line-square" d="M48 134Q235 132 356 18"/><text class="viz-legend" x="70" y="34">O(1)</text><text class="viz-legend" x="120" y="50">O(log n)</text><text class="viz-legend" x="191" y="71">O(n)</text><text class="viz-legend" x="260" y="52">O(n log n)</text><text class="viz-legend" x="310" y="25">O(n²)</text>'
    },
    'sliding-window': {
      title: 'Two pointers · sliding window', alt: 'A contiguous window spans values between a left pointer and a right pointer.',
      svg: '<text class="viz-note" x="98" y="32">left</text><text class="viz-note" x="270" y="32">right</text><path class="viz-accent-stroke" d="M99 36v10m-5-5 5 5 5-5M270 36v10m-5-5 5 5 5-5"/><g class="viz-cells"><rect x="22" y="52" width="54" height="48" rx="8"/><rect class="viz-highlight" x="80" y="52" width="54" height="48" rx="8"/><rect class="viz-highlight" x="138" y="52" width="54" height="48" rx="8"/><rect class="viz-highlight" x="196" y="52" width="54" height="48" rx="8"/><rect x="254" y="52" width="54" height="48" rx="8"/><rect x="312" y="52" width="54" height="48" rx="8"/></g><g class="viz-values"><text x="49" y="82">4</text><text x="107" y="82">2</text><text x="165" y="82">7</text><text x="223" y="82">1</text><text x="281" y="82">5</text><text x="339" y="82">3</text></g><text class="viz-note" x="194" y="131">expand or shrink the window</text>'
    },
    'dynamic-programming': {
      title: 'Dynamic programming · reuse subproblems', alt: 'A table stores earlier results so overlapping subproblems are not recomputed.',
      svg: '<text class="viz-label" x="195" y="30">Fibonacci example</text><g class="viz-index"><text x="66" y="54">n</text><text x="150" y="54">0</text><text x="204" y="54">1</text><text x="258" y="54">2</text><text x="312" y="54">3</text></g><g class="viz-cells"><rect x="44" y="62" width="50" height="30" rx="5"/><rect x="98" y="62" width="50" height="30" rx="5"/><rect x="152" y="62" width="50" height="30" rx="5"/><rect x="206" y="62" width="50" height="30" rx="5"/><rect x="260" y="62" width="50" height="30" rx="5"/><rect x="314" y="62" width="50" height="30" rx="5"/></g><g class="viz-values"><text x="69" y="82">F(n)</text><text x="123" y="82">0</text><text x="177" y="82">1</text><text x="231" y="82">1</text><text x="285" y="82">2</text><text x="339" y="82">3</text></g><path class="viz-link" d="M177 105L230 124M231 105L284 124M285 105L338 124"/><text class="viz-note" x="195" y="145">store once · reuse many times</text>'
    },
    recursion: {
      title: 'Recursion · smaller calls and a base case', alt: 'A recursive call expands into smaller calls until a base case, then returns.',
      svg: '<path class="viz-link" d="M194 49L112 92M194 49L276 92M112 109L72 139M112 109L152 139"/><g class="viz-node"><circle cx="194" cy="43" r="24"/><circle cx="112" cy="98" r="22"/><circle cx="276" cy="98" r="22"/><circle cx="72" cy="143" r="18"/><circle cx="152" cy="143" r="18"/></g><g class="viz-values"><text x="194" y="47">call</text><text x="112" y="102">smaller</text><text x="276" y="102">return</text><text x="72" y="147">base</text><text x="152" y="147">base</text></g>'
    },
    trie: {
      title: 'Trie · shared prefixes', alt: 'Words share prefix nodes in a trie; terminal nodes mark complete words.',
      svg: '<path class="viz-link" d="M194 38L120 82M194 38L268 82M120 98L82 135M120 98L158 135M268 98L268 135"/><g class="viz-node"><circle cx="194" cy="32" r="18"/><circle cx="120" cy="88" r="18"/><circle cx="268" cy="88" r="18"/><circle cx="82" cy="140" r="18"/><circle cx="158" cy="140" r="18"/><circle cx="268" cy="140" r="18"/></g><g class="viz-values"><text x="194" y="36">root</text><text x="120" y="92">c</text><text x="268" y="92">d</text><text x="82" y="144">a</text><text x="158" y="144">t*</text><text x="268" y="144">og*</text></g><text class="viz-note" x="196" y="166">* marks a complete word</text>'
    },
    'range-trees': {
      title: 'Range-query structures', alt: 'A parent range node covers two child ranges, which cover smaller intervals.',
      svg: '<path class="viz-link" d="M195 43L112 88M195 43L278 88M112 105L68 137M112 105L156 137M278 105L244 137M278 105L318 137"/><g class="viz-node"><circle cx="195" cy="38" r="19"/><circle cx="112" cy="94" r="19"/><circle cx="278" cy="94" r="19"/><circle cx="68" cy="142" r="17"/><circle cx="156" cy="142" r="17"/><circle cx="244" cy="142" r="17"/><circle cx="318" cy="142" r="17"/></g><g class="viz-values"><text x="195" y="42">0–7</text><text x="112" y="98">0–3</text><text x="278" y="98">4–7</text><text x="68" y="146">0–1</text><text x="156" y="146">2–3</text><text x="244" y="146">4–5</text><text x="318" y="146">6–7</text></g>'
    },
    'union-find': {
      title: 'Union-find · connected components', alt: 'Two sets each have a representative root; union merges components.',
      svg: '<path class="viz-link" d="M92 60L58 105M92 60L126 105M294 60L260 105M294 60L328 105"/><g class="viz-node"><circle cx="92" cy="55" r="22"/><circle cx="58" cy="110" r="18"/><circle cx="126" cy="110" r="18"/><circle cx="294" cy="55" r="22"/><circle cx="260" cy="110" r="18"/><circle cx="328" cy="110" r="18"/></g><g class="viz-values"><text x="92" y="59">root A</text><text x="58" y="114">x</text><text x="126" y="114">y</text><text x="294" y="59">root B</text><text x="260" y="114">z</text><text x="328" y="114">w</text></g><path class="viz-accent-stroke" d="M151 82h80m-8-7 8 7-8 7"/><text class="viz-note" x="192" y="154">union(A, B)</text>'
    },
    'dijkstra': {
      title: 'Dijkstra · shortest paths', alt: 'Weighted graph with distances updated outward from the source vertex.',
      svg: '<path class="viz-link" d="M76 78L182 43M76 78L129 135M182 43L292 78M182 43L237 135M129 135L237 135M237 135L292 78"/><g class="viz-node viz-node-visited"><circle cx="76" cy="78" r="24"/><circle cx="182" cy="43" r="24"/><circle cx="292" cy="78" r="24"/><circle cx="129" cy="135" r="24"/><circle cx="237" cy="135" r="24"/></g><g class="viz-values"><text x="76" y="74">A</text><text x="76" y="89">0</text><text x="182" y="39">B</text><text x="182" y="54">2</text><text x="292" y="74">C</text><text x="292" y="89">4</text><text x="129" y="131">D</text><text x="129" y="146">3</text><text x="237" y="131">E</text><text x="237" y="146">5</text></g><text class="viz-note" x="192" y="164">nonnegative edge weights</text>'
    },
    anagram: {
      title: 'Anagram · compare character counts', alt: 'The words listen and silent have matching character counts.',
      svg: '<text class="viz-label" x="98" y="36">listen</text><text class="viz-label" x="291" y="36">silent</text><g class="viz-cells"><rect x="28" y="49" width="300" height="32" rx="7"/><rect x="28" y="87" width="300" height="32" rx="7"/></g><g class="viz-values"><text x="178" y="70">e:1 · i:1 · l:1 · n:1 · s:1 · t:1</text><text x="178" y="108">e:1 · i:1 · l:1 · n:1 · s:1 · t:1</text></g><path class="viz-accent-stroke" d="M345 67v33m-7-8 7 8 7-8"/><text class="viz-note" x="195" y="145">same counts → anagrams</text>'
    },
    parentheses: {
      title: 'Balanced brackets · stack trace', alt: 'Opening brackets are pushed onto a stack and matching closing brackets pop them.',
      svg: '<text class="viz-label" x="93" y="33">input: ( [ ] )</text><path class="viz-link" d="M127 49v18m45-18v18m45-18v18m45-18v18"/><g class="viz-cells"><rect x="99" y="72" width="54" height="35" rx="7"/><rect x="99" y="111" width="54" height="35" rx="7"/></g><g class="viz-values"><text x="126" y="95">[</text><text x="126" y="134">(</text></g><text class="viz-note" x="251" y="91">close bracket pops opener</text><text class="viz-note" x="251" y="129">empty stack means balanced</text>'
    },
    'word-ladder': {
      title: 'Word ladder · BFS layers', alt: 'Breadth-first search explores one edit-distance layer at a time from cold to warm.',
      svg: '<path class="viz-link" d="M65 85h67m-7-6 7 6-7 6M162 85h67m-7-6 7 6-7 6M259 85h67m-7-6 7 6-7 6"/><g class="viz-node viz-node-visited"><circle cx="48" cy="85" r="23"/><circle cx="145" cy="85" r="23"/><circle cx="242" cy="85" r="23"/><circle cx="339" cy="85" r="23"/></g><g class="viz-values"><text x="48" y="89">cold</text><text x="145" y="89">cord</text><text x="242" y="89">card</text><text x="339" y="89">ward</text></g><text class="viz-note" x="194" y="138">visit by distance from start</text>'
    },
  };

  function render(key) {
    const item = diagrams[key];
    if (!item) return '';
    return '<figure class="visual-card"><figcaption><strong>' + item.title + '</strong><span>Visual guide</span></figcaption><svg viewBox="0 0 400 180" role="img" aria-label="' + item.alt + '" xmlns="http://www.w3.org/2000/svg">' + item.svg + '</svg></figure>';
  }

  window.PyPalVisuals = { render };
})();
