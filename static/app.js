const form = document.querySelector('#chat-form');
const input = document.querySelector('#question');
const sendButton = document.querySelector('#send-button');
const messages = document.querySelector('#messages');
const welcome = document.querySelector('#welcome');
const count = document.querySelector('#char-count');
const themeToggle = document.querySelector('#theme-toggle');
let busy = false;

function setTheme(theme) {
  const isDark = theme !== 'light';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  themeToggle.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
  themeToggle.innerHTML = isDark
    ? '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="3.5"/><path d="M10 1.8v2m0 12.4v2M1.8 10h2m12.4 0h2M4.2 4.2l1.4 1.4m8.8 8.8 1.4 1.4m0-11.6-1.4 1.4m-8.8 8.8-1.4 1.4"/></svg>'
    : '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M17.2 12.4A7.5 7.5 0 0 1 7.6 2.8a7.6 7.6 0 1 0 9.6 9.6Z"/></svg>';
}
setTheme(localStorage.getItem('pypal-theme') || 'dark');
themeToggle.addEventListener('click', () => {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('pypal-theme', nextTheme);
  setTheme(nextTheme);
});

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
const knowledgePageLabel = document.querySelector('#knowledge-page');
const knowledgePrevious = document.querySelector('#knowledge-prev');
const knowledgeNext = document.querySelector('#knowledge-next');
const knowledgePageSize = 40;
let knowledgeEntries = [];
let knowledgePage = 0;

function renderKnowledgeEntries() {
  const query = knowledgeSearch.value.trim().toLowerCase();
  const filtered = knowledgeEntries.filter((entry) => !query || (entry.question + ' ' + entry.answer).toLowerCase().includes(query));
  const pageCount = Math.ceil(filtered.length / knowledgePageSize);
  knowledgePage = Math.min(knowledgePage, Math.max(0, pageCount - 1));
  const start = knowledgePage * knowledgePageSize;
  const pageEntries = filtered.slice(start, start + knowledgePageSize);
  knowledgeList.scrollTop = 0;
  knowledgeResultsCount.textContent = filtered.length
    ? query ? `${start + 1}–${Math.min(start + knowledgePageSize, filtered.length)} of ${filtered.length} matches` : `${start + 1}–${Math.min(start + knowledgePageSize, filtered.length)} of ${filtered.length} topics`
    : query ? '0 matching topics' : '0 topics';
  knowledgePageLabel.textContent = `${pageCount ? knowledgePage + 1 : 0} / ${pageCount}`;
  knowledgePrevious.disabled = knowledgePage === 0 || pageCount === 0;
  knowledgeNext.disabled = knowledgePage >= pageCount - 1;
  knowledgeList.innerHTML = pageEntries.length ? pageEntries.map((entry) => {
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
knowledgeSearch.addEventListener('input', () => { knowledgePage = 0; renderKnowledgeEntries(); });
knowledgePrevious.addEventListener('click', () => { if (knowledgePage > 0) { knowledgePage -= 1; renderKnowledgeEntries(); } });
knowledgeNext.addEventListener('click', () => { knowledgePage += 1; renderKnowledgeEntries(); });
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
