import { StrictMode } from "react";
import { FormEvent, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import {
  addTodo,
  adoptBreakdownTasks,
  applyBreakdownError,
  initialWorkspaceState,
  startBreakdownRequest,
  toggleTodo,
  updateTodoAcceptanceCriteria,
  updateTodoDescription,
  updateTodoTitle,
  type BreakdownTask,
  type WorkspaceState,
} from "./workspaceState";

type BreakdownResponse = {
  provider: string;
  model: string;
  prompt_version: string;
  breakdown_run_id: number | null;
  tasks: BreakdownTask[];
};

const exampleGoals = [
  "Launch a small portfolio site in two weeks",
  "Prepare a first user interview for Koma Planner",
  "Clean up my backlog before Friday",
];

function App() {
  const [goalText, setGoalText] = useState("");
  const [workspace, setWorkspace] = useState<WorkspaceState>(initialWorkspaceState);
  const [formMessage, setFormMessage] = useState("");

  const completedCount = useMemo(() => workspace.todos.filter((todo) => todo.completed).length, [workspace.todos]);
  const canSubmit = goalText.trim().length > 0 && workspace.status !== "loading";

  async function handleBreakdown(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedGoal = goalText.trim();
    if (!trimmedGoal) {
      setFormMessage("Enter a goal before requesting a breakdown.");
      return;
    }

    setFormMessage("");
    const loadingState = startBreakdownRequest(trimmedGoal);
    setWorkspace(loadingState);

    try {
      const response = await fetch("/api/breakdowns", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ goal_text: trimmedGoal }),
      });

      if (!response.ok) {
        throw new Error(`Breakdown request failed with ${response.status}`);
      }

      const breakdown = (await response.json()) as BreakdownResponse;
      setWorkspace(adoptBreakdownTasks(loadingState, breakdown.tasks));
    } catch (error) {
      setWorkspace(applyBreakdownError(loadingState, error));
    }
  }

  function updateWorkspace(nextState: WorkspaceState) {
    setWorkspace(nextState);
  }

  return (
    <main className="app-shell">
      <header className="topbar" aria-label="Workspace header">
        <div>
          <p className="product-name">Koma Planner</p>
          <h1>Goal breakdown workspace</h1>
        </div>
        <div className="workspace-meter" aria-label="Todo progress">
          <span>{completedCount}</span>
          <span>/</span>
          <span>{workspace.todos.length}</span>
        </div>
      </header>

      <section className="workspace">
        <form className="goal-panel" onSubmit={handleBreakdown}>
          <div className="panel-heading">
            <label htmlFor="goal">Goal</label>
            <span className="status-pill" data-status={workspace.status}>
              {workspace.status === "idle" ? "Ready" : workspace.status}
            </span>
          </div>
          <textarea
            id="goal"
            name="goal"
            rows={8}
            value={goalText}
            onChange={(event) => setGoalText(event.target.value)}
            placeholder="Example: Launch a small web app for AI-assisted todo breakdowns"
          />
          {formMessage ? <p className="form-message">{formMessage}</p> : null}
          <div className="example-row" aria-label="Example goals">
            {exampleGoals.map((goal) => (
              <button key={goal} type="button" className="example-button" onClick={() => setGoalText(goal)}>
                {goal}
              </button>
            ))}
          </div>
          <button className="primary-action" type="submit" disabled={!canSubmit}>
            {workspace.status === "loading" ? "Breaking down..." : "Break down goal"}
          </button>
        </form>

        <section className="todo-workspace" aria-live="polite">
          <div className="workspace-heading">
            <div>
              <p className="section-label">Todos</p>
              <h2>{workspace.goalText || "Start with a rough goal"}</h2>
            </div>
            <button
              type="button"
              className="secondary-action"
              onClick={() => updateWorkspace(addTodo(workspace))}
              disabled={workspace.status === "loading"}
            >
              Add task
            </button>
          </div>

          <WorkspaceStateView workspace={workspace} onWorkspaceChange={updateWorkspace} />
        </section>
      </section>
    </main>
  );
}

type WorkspaceStateViewProps = {
  workspace: WorkspaceState;
  onWorkspaceChange: (state: WorkspaceState) => void;
};

function WorkspaceStateView({ workspace, onWorkspaceChange }: WorkspaceStateViewProps) {
  if (workspace.status === "loading") {
    return (
      <div className="state-panel" role="status">
        <div className="loader" aria-hidden="true" />
        <p>Creating a task breakdown...</p>
      </div>
    );
  }

  if (workspace.status === "error") {
    return (
      <div className="state-panel error-panel" role="alert">
        <p>{workspace.errorMessage}</p>
      </div>
    );
  }

  if (workspace.status === "empty") {
    return (
      <div className="state-panel">
        <p>No tasks came back for this goal. Try adding one manually or make the goal more specific.</p>
      </div>
    );
  }

  if (workspace.todos.length === 0) {
    return (
      <div className="state-panel">
        <p>Your generated todos will appear here as soon as the breakdown is ready.</p>
      </div>
    );
  }

  return (
    <ol className="todo-list">
      {workspace.todos.map((todo) => (
        <li key={todo.id} className="todo-item">
          <label className="check-control">
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => onWorkspaceChange(toggleTodo(workspace, todo.id))}
            />
            <span>{todo.completed ? "Done" : "Todo"}</span>
          </label>
          <div className="todo-fields">
            <input
              aria-label="Task title"
              className="title-input"
              value={todo.title}
              onChange={(event) => onWorkspaceChange(updateTodoTitle(workspace, todo.id, event.target.value))}
              placeholder="Task title"
            />
            <textarea
              aria-label="Task description"
              value={todo.description}
              onChange={(event) => onWorkspaceChange(updateTodoDescription(workspace, todo.id, event.target.value))}
              placeholder="Notes"
              rows={2}
            />
            <textarea
              aria-label="Acceptance criteria"
              value={todo.acceptanceCriteria}
              onChange={(event) =>
                onWorkspaceChange(updateTodoAcceptanceCriteria(workspace, todo.id, event.target.value))
              }
              placeholder="Acceptance criteria"
              rows={2}
            />
          </div>
        </li>
      ))}
    </ol>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
