import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <p className="eyebrow">Koma Planner</p>
          <h1>Turn a rough goal into todos you can start now.</h1>
          <p>
            This scaffold is ready for the MVP flow: goal input, AI breakdown,
            editable tasks, and saved projects.
          </p>
        </div>

        <form className="goal-panel">
          <label htmlFor="goal">Goal</label>
          <textarea
            id="goal"
            name="goal"
            rows={6}
            placeholder="Example: Launch a small web app for AI-assisted todo breakdowns"
          />
          <button type="button">Break down goal</button>
        </form>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
