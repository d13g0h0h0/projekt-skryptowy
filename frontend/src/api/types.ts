type TaskId = string & { __brand: "task" };
type UserId = string & { __brand: "user" };

export type Author = {
  id: UserId
  username: string
}

export type Subtask = {
  id: TaskId
  content: string
}

//TODO: check out Zod for better type enforcement from parsed JSON
export type Task = {
  id: TaskId
  title: string
  content: string
  author: Author
  created_at: Date,
  updated_at: Date,
  subtasks?: Subtask[]
}