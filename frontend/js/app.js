const form = document.querySelector('#todo-form');
const input = document.querySelector('#todo-input');
const list = document.querySelector('#todo-list');
const status = document.querySelector('#status');
let todos = [];
let busy = false;

async function api(path = '', options = {}) {
  const response = await fetch(`/api/todos${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || '요청을 처리하지 못했습니다.');
  return data;
}

function render() {
  list.replaceChildren();
  for (const todo of todos) {
    const item = document.createElement('li');
    item.classList.toggle('completed', todo.completed);
    const label = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = todo.completed;
    checkbox.disabled = busy;
    checkbox.addEventListener('change', () => change(async () => {
      const updated = await api(`/${todo.id}`, { method: 'PATCH', body: JSON.stringify({ completed: checkbox.checked }) });
      todos = todos.map((entry) => entry.id === updated.id ? updated : entry);
    }));
    const title = document.createElement('span');
    title.textContent = todo.title;
    label.append(checkbox, title);
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'delete';
    remove.textContent = '삭제';
    remove.setAttribute('aria-label', `${todo.title} 삭제`);
    remove.disabled = busy;
    remove.addEventListener('click', () => change(async () => {
      await api(`/${todo.id}`, { method: 'DELETE' });
      todos = todos.filter((entry) => entry.id !== todo.id);
    }));
    item.append(label, remove);
    list.append(item);
  }
  document.querySelector('#empty').hidden = todos.length !== 0;
  document.querySelector('#count').textContent = `${todos.filter((todo) => todo.completed).length} / ${todos.length} 완료`;
  form.querySelector('button').disabled = busy;
  input.disabled = busy;
}

async function change(action) {
  if (busy) return;
  busy = true;
  status.textContent = '';
  // Keep existing controls while the request is pending.
  document.querySelectorAll('button, input').forEach((control) => { control.disabled = true; });
  try { await action(); }
  catch (error) { status.textContent = error.message; }
  finally { busy = false; render(); }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) { status.textContent = '할 일을 입력해 주세요.'; input.focus(); return; }
  await change(async () => {
    const todo = await api('', { method: 'POST', body: JSON.stringify({ title }) });
    todos.push(todo);
    input.value = '';
  });
  input.focus();
});
change(async () => { todos = await api(); });
