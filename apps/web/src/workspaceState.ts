export type WorkspaceStatus = "idle" | "loading" | "empty" | "success" | "error";

export type BreakdownTask = {
  title: string;
  description: string | null;
  acceptance_criteria: string | null;
  position: number;
  estimate_minutes: number | null;
};

export type TodoItem = {
  id: string;
  title: string;
  description: string;
  acceptanceCriteria: string;
  estimateMinutes: number | null;
  completed: boolean;
  position: number;
};

export type WorkspaceState = {
  status: WorkspaceStatus;
  goalText: string;
  todos: TodoItem[];
  errorMessage: string;
};

export const initialWorkspaceState: WorkspaceState = {
  status: "idle",
  goalText: "",
  todos: [],
  errorMessage: "",
};

const friendlyBreakdownError = "We could not break down that goal. Please adjust the goal and try again.";

export function startBreakdownRequest(goalText: string): WorkspaceState {
  return {
    status: "loading",
    goalText: goalText.trim(),
    todos: [],
    errorMessage: "",
  };
}

export function adoptBreakdownTasks(state: WorkspaceState, tasks: BreakdownTask[]): WorkspaceState {
  const todos = tasks
    .slice()
    .sort((left, right) => left.position - right.position)
    .map((task, index) => createTodo(task, index));

  return {
    ...state,
    status: todos.length > 0 ? "success" : "empty",
    todos,
    errorMessage: "",
  };
}

export function applyBreakdownError(state: WorkspaceState, _error: unknown): WorkspaceState {
  return {
    ...state,
    status: "error",
    errorMessage: friendlyBreakdownError,
  };
}

export function addTodo(state: WorkspaceState): WorkspaceState {
  const position = state.todos.length;
  return {
    ...state,
    status: "success",
    todos: [
      ...state.todos,
      {
        id: `local-${Date.now()}-${position}`,
        title: "",
        description: "",
        acceptanceCriteria: "",
        estimateMinutes: null,
        completed: false,
        position,
      },
    ],
  };
}

export function updateTodoTitle(state: WorkspaceState, todoId: string, title: string): WorkspaceState {
  return updateTodo(state, todoId, (todo) => ({ ...todo, title }));
}

export function updateTodoDescription(state: WorkspaceState, todoId: string, description: string): WorkspaceState {
  return updateTodo(state, todoId, (todo) => ({ ...todo, description }));
}

export function updateTodoAcceptanceCriteria(
  state: WorkspaceState,
  todoId: string,
  acceptanceCriteria: string,
): WorkspaceState {
  return updateTodo(state, todoId, (todo) => ({ ...todo, acceptanceCriteria }));
}

export function toggleTodo(state: WorkspaceState, todoId: string): WorkspaceState {
  return updateTodo(state, todoId, (todo) => ({ ...todo, completed: !todo.completed }));
}

export function deleteTodo(state: WorkspaceState, todoId: string): WorkspaceState {
  const todos = state.todos
    .filter((todo) => todo.id !== todoId)
    .map((todo, position) => ({ ...todo, position }));

  return {
    ...state,
    status: todos.length > 0 ? state.status : "empty",
    todos,
  };
}

function updateTodo(state: WorkspaceState, todoId: string, update: (todo: TodoItem) => TodoItem): WorkspaceState {
  return {
    ...state,
    todos: state.todos.map((todo) => (todo.id === todoId ? update(todo) : todo)),
  };
}

function createTodo(task: BreakdownTask, index: number): TodoItem {
  return {
    id: `generated-${task.position}-${index}`,
    title: task.title,
    description: task.description ?? "",
    acceptanceCriteria: task.acceptance_criteria ?? "",
    estimateMinutes: task.estimate_minutes,
    completed: false,
    position: index,
  };
}
