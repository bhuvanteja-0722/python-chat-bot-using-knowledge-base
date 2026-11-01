const form = document.querySelector('#chat-form');
const input = document.querySelector('#question');
const sendButton = document.querySelector('#send-button');
const messages = document.querySelector('#messages');
const welcome = document.querySelector('#welcome');
const count = document.querySelector('#char-count');
let busy = false;

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function formatAnswer(text) {
  const codeBlocks = [];
  let safe = escapeHtml(text).replace(/```(?:python)?\n([\s\S]*?)```/g, (_, code) => {
    codeBlocks.push('<pre><code>' + code.trimEnd() + '</code></pre>');
    return '\u0000' + (codeBlocks.length - 1) + '\u0000';
  });
  safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
  return safe.split(/\n\n+/).map((part) => part.split(/\u0000(\d+)\u0000/g).map((segment, index) => {
    if (index % 2) return codeBlocks[Number(segment)];
    return segment.trim() ? '<p>' + segment.replace(/\n/g, '<br>') + '</p>' : '';
  }).join('')).join('');
}

function appendMessage(role, text, typing = false, visualKey = null) {
  const article = document.createElement('article');
  article.className = 'message ' + role;
  const avatar = role === 'bot' ? 'Py' : 'Y';
  const label = role === 'bot' ? 'Python helper' : 'You';
  const body = typing
    ? '<div class="typing" aria-label="Thinking"><span></span><span></span><span></span></div>'
    : '<div class="message-bubble">' + (role === 'bot' ? formatAnswer(text) : escapeHtml(text).replace(/\n/g, '<br>')) + (role === 'bot' && visualKey && window.PyPalVisuals ? window.PyPalVisuals.render(visualKey) : '') + '</div>';
  article.innerHTML = '<span class="message-avatar" aria-hidden="true">' + avatar + '</span><div class="message-content"><div class="message-meta">' + label + '</div>' + body + '</div>';
  messages.append(article);
  scrollToLatest();
  return article;
}

function scrollToLatest() {
  const conversation = document.querySelector('.conversation');
  requestAnimationFrame(() => {
    conversation.scrollTo({
      top: conversation.scrollHeight,
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
  });
}

function updateComposer() {
  const value = input.value;
  sendButton.disabled = !value.trim() || busy;
  count.textContent = value.length.toLocaleString() + ' / 2,000';
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 130) + 'px';
}

async function ask(question) {
  const trimmed = question.trim();
  if (!trimmed || busy) return;
  welcome.hidden = true;
  appendMessage('user', trimmed);
  input.value = '';
  busy = true;
  updateComposer();
  const thinking = appendMessage('bot', '', true);
  try {
    const response = await fetch('/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: trimmed }),
    });
    const data = await response.json();
    thinking.remove();
    if (!response.ok) throw new Error(data.error || 'Could not get an answer. Please try again.');
    appendMessage('bot', data.answer, false, data.visual);
  } catch (error) {
    thinking.remove();
    appendMessage('bot', error.message || 'Could not reach the local chatbot. Make sure the server is running and try again.');
  } finally {
    busy = false;
    updateComposer();
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  ask(input.value);
});
input.addEventListener('input', updateComposer);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll('[data-question]').forEach((button) => {
  button.addEventListener('click', () => ask(button.dataset.question));
});
function resetChat() {
  messages.replaceChildren();
  welcome.hidden = false;
  input.value = '';
  updateComposer();
  input.focus();
}
document.querySelector('#new-chat').addEventListener('click', resetChat);
document.querySelector('#clear-chat').addEventListener('click', resetChat);
const knowledgeDialog = document.querySelector('#knowledge-dialog');
const knowledgeList = document.querySelector('#knowledge-list');
const knowledgeSearch = document.querySelector('#knowledge-search');
const knowledgeResultsCount = document.querySelector('#knowledge-results-count');
let knowledgeEntries = [];

function renderKnowledgeEntries() {
  const query = knowledgeSearch.value.trim().toLowerCase();
  const filtered = knowledgeEntries.filter((entry) => !query || (entry.question + ' ' + entry.answer).toLowerCase().includes(query));
  knowledgeList.scrollTop = 0;
  knowledgeResultsCount.textContent = query ? `${filtered.length} of ${knowledgeEntries.length} topics` : `${knowledgeEntries.length} topics`;
  knowledgeList.innerHTML = filtered.length ? filtered.map((entry) => {
    const visual = entry.visual && window.PyPalVisuals ? window.PyPalVisuals.render(entry.visual) : '';
    return '<details class="knowledge-entry"><summary><span>' + escapeHtml(entry.question) + '</span><span class="knowledge-entry-chevron" aria-hidden="true">⌄</span></summary><div class="knowledge-answer"><div class="knowledge-answer-copy">' + formatAnswer(entry.answer) + '</div>' + visual + '<button class="knowledge-ask" type="button" data-ask-question="' + escapeHtml(entry.question) + '">Ask this question <span aria-hidden="true">↗</span></button></div></details>';
  }).join('') : '<div class="knowledge-empty"><strong>No matching topics</strong><span>Try a broader Python term.</span></div>';
}

async function openKnowledgeBase() {
  knowledgeDialog.showModal();
  knowledgeSearch.focus();
  if (knowledgeEntries.length) return;
  knowledgeResultsCount.textContent = 'Loading topics…';
  try {
    const response = await fetch('/api/knowledge', { cache: 'no-store' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to load the knowledge base.');
    knowledgeEntries = data.entries.sort((a, b) => a.question.localeCompare(b.question));
    document.querySelector('#knowledge-count').textContent = data.count;
    renderKnowledgeEntries();
  } catch (error) {
    knowledgeResultsCount.textContent = 'Could not load topics';
    knowledgeList.innerHTML = '<div class="knowledge-empty"><strong>Knowledge base unavailable</strong><span>' + escapeHtml(error.message || 'Please try again.') + '</span><button class="knowledge-ask" id="retry-knowledge" type="button">Try again</button></div>';
  }
}

document.querySelector('#open-knowledge').addEventListener('click', openKnowledgeBase);
document.querySelector('#close-knowledge').addEventListener('click', () => knowledgeDialog.close());
knowledgeSearch.addEventListener('input', renderKnowledgeEntries);
knowledgeList.addEventListener('click', (event) => {
  const askButton = event.target.closest('[data-ask-question]');
  if (askButton) {
    const question = askButton.dataset.askQuestion;
    knowledgeDialog.close();
    ask(question);
  } else if (event.target.closest('#retry-knowledge')) {
    knowledgeEntries = [];
    openKnowledgeBase();
  }
});
knowledgeDialog.addEventListener('click', (event) => {
  if (event.target === knowledgeDialog) knowledgeDialog.close();
});
document.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    resetChat();
  }
  if (knowledgeDialog.open && (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'f') {
    event.preventDefault();
    knowledgeSearch.focus();
  }
});
updateComposer();
