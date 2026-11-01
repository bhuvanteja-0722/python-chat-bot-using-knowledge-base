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
document.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    resetChat();
  }
});
updateComposer();
