const list = document.querySelector('#exerciseList');
const title = document.querySelector('#exerciseTitle');
const promptBox = document.querySelector('#exercisePrompt');
const hints = document.querySelector('#hints');
const tag = document.querySelector('#skillTag');
const answer = document.querySelector('#answer');
const result = document.querySelector('#result');
const submit = document.querySelector('#submitBtn');
let exercises = [];
let current = null;

function renderExercise(exercise) {
  current = exercise;
  title.textContent = exercise.title;
  promptBox.textContent = exercise.prompt;
  tag.textContent = exercise.skill;
  answer.value = '';
  result.classList.add('hidden');
  hints.innerHTML = exercise.hints.map((hint) => `<li>${hint}</li>`).join('');
  document.querySelectorAll('.exercise').forEach((button) => {
    button.classList.toggle('active', Number(button.dataset.id) === exercise.id);
  });
}

async function loadExercises() {
  const response = await fetch('/api/exercises');
  exercises = await response.json();
  list.innerHTML = exercises.map((exercise) => `
    <button class="exercise" data-id="${exercise.id}">
      <strong>${exercise.title}</strong><br />
      <small>${exercise.skill}</small>
    </button>
  `).join('');
  list.addEventListener('click', (event) => {
    const button = event.target.closest('.exercise');
    if (!button) return;
    renderExercise(exercises.find((exercise) => exercise.id === Number(button.dataset.id)));
  });
  renderExercise(exercises[0]);
}

submit.addEventListener('click', async () => {
  if (!answer.value.trim()) {
    result.classList.remove('hidden');
    result.innerHTML = '<strong>请先输入答案。</strong>';
    return;
  }
  submit.disabled = true;
  const response = await fetch('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exercise_id: current.id, answer: answer.value }),
  });
  const data = await response.json();
  submit.disabled = false;
  result.classList.remove('hidden');
  result.innerHTML = `
    <div class="score">${data.score}/100</div>
    <p><strong>等级：</strong>${data.band}</p>
    <ul>${data.feedback.map((item) => `<li>${item}</li>`).join('')}</ul>
    <p><strong>建议改写：</strong>${data.suggested_revision}</p>
  `;
});

loadExercises();
