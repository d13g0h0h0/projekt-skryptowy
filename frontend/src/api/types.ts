type TaskId = string & { __brand: "task" };
type SubTaskId = string & { __brand: "subtask" };
type UserId = string & { __brand: "user" };

export type Author = {
  id: UserId
  username: string
};

export type Subtask = {
  id: SubTaskId
  content: string
};

//TODO: check out Zod for better type enforcement from parsed JSON
export type Task = {
  id: TaskId
  title: string
  content: string
  author: Author
  created_at: Date,
  updated_at: Date,
  subtasks?: Subtask[]
};

export type CreateTaskInput = Pick<Task, "title" | "content">;