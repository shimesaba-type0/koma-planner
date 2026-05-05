import assert from "node:assert/strict";
import {
  addTodo,
  adoptBreakdownTasks,
  applyBreakdownError,
  deleteTodo,
  startBreakdownRequest,
  toggleTodo,
  updateTodoTitle,
  type WorkspaceState,
} from "../src/workspaceState.ts";

const state = startBreakdownRequest("  Launch a small workshop  ");

assert.equal(state.status, "loading");
assert.equal(state.goalText, "Launch a small workshop");
assert.deepEqual(state.todos, []);
assert.equal(state.errorMessage, "");

const loading = startBreakdownRequest("Build a release checklist");
const success = adoptBreakdownTasks(loading, [
  {
    title: "List release blockers",
    description: "Check bugs, docs, and deployment risks",
    acceptance_criteria: "Each blocker has an owner",
    position: 0,
    estimate_minutes: 20,
  },
  {
    title: "Ship the release",
    description: null,
    acceptance_criteria: null,
    position: 1,
    estimate_minutes: null,
  },
]);

assert.equal(success.status, "success");
assert.equal(success.todos.length, 2);
assert.equal(success.todos[0]?.title, "List release blockers");
assert.equal(success.todos[0]?.completed, false);
assert.equal(success.todos[0]?.acceptanceCriteria, "Each blocker has an owner");
assert.equal(success.todos[1]?.description, "");

const empty = adoptBreakdownTasks(startBreakdownRequest("Plan"), []);

assert.equal(empty.status, "empty");
assert.deepEqual(empty.todos, []);

const errorState = applyBreakdownError(startBreakdownRequest("Plan"), new Error("stack trace and backend internals"));

assert.equal(errorState.status, "error");
assert.equal(errorState.errorMessage, "We could not break down that goal. Please adjust the goal and try again.");

const initial: WorkspaceState = adoptBreakdownTasks(startBreakdownRequest("Plan"), [
  {
    title: "Draft plan",
    description: null,
    acceptance_criteria: null,
    position: 0,
    estimate_minutes: null,
  },
]);

const added = addTodo(initial);
const renamed = updateTodoTitle(added, added.todos[1]!.id, "Ask for feedback");
const toggled = toggleTodo(renamed, renamed.todos[0]!.id);
const deleted = deleteTodo(toggled, toggled.todos[0]!.id);

assert.equal(added.todos.length, 2);
assert.equal(renamed.todos[1]?.title, "Ask for feedback");
assert.equal(toggled.todos[0]?.completed, true);
assert.equal(deleted.todos.length, 1);
assert.equal(deleted.todos[0]?.title, "Ask for feedback");
