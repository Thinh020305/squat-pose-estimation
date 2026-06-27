async function stopWorkout() {
  const response = await fetch("/workout/stop", { method: "POST" });
  if (response.ok) {
    window.location.href = "/history";
  }
}

async function refreshWorkoutStatus() {
  const node = document.querySelector("[data-workout-status]");
  if (!node) return;
  const response = await fetch("/workout/status");
  if (!response.ok) return;
  const data = await response.json();
  node.textContent =
    `Reps: ${data.reps} | Score: ${data.score} | ${data.label || "waiting"} | ${data.feedback || ""}`;
}

setInterval(refreshWorkoutStatus, 1000);
