export type TaskId = string & { __brand: "task" };
export type SubTaskId = string & { __brand: "subtask" };
export type UserId = string & { __brand: "user" };
export type SolutionId = string & { __brand: "solution" };
export type SolutionPartId = string & { __brand: "solution_part" };
export type VoteId = string & { __brand: "vote" };

export type Author = {
  id: UserId
  username: string
};

export type SubTask = {
  id: SubTaskId
  content: string
};

export type CreateSubTaskInput = Pick<SubTask, "content">;

//TODO: check out Zod for better type enforcement from parsed JSON
export type Task = {
  id: TaskId
  title: string
  content: string
  author: Author
  created_at: Date,
  updated_at: Date,
  subtasks: SubTask[]
};

export type CreateTaskInput = Pick<Task, "title" | "content"> & { subtasks: CreateSubTaskInput[]};

export type SolutionPart = {
  id: SolutionPartId
  subtask_id: SubTaskId
  content: string
};

export type CreateSolutionPartInput = Pick<SolutionPart, "content" | "subtask_id">;

export type VoteValueEnum = 1 | -1;

export type Vote = {
  id: VoteId
  user: Author
  value: VoteValueEnum
  created_at: Date
};

export type CreateVoteInput = Pick<Vote, "value">;

export type Solution = {
  id: SolutionId
  content: string
  author: Author
  created_at: Date
  updated_at: Date
  score: number
  my_vote: VoteValueEnum | null
  parts?: SolutionPart[]
};

export type CreateSolutionInput = Pick<Solution, "content" | "parts">;

export type RoleEnum = "student" | "teacher"

export type User = {
  id: UserId
  username: string
  email: string
  scopes: string[]
  role: RoleEnum
};

export type LoginInput = {
  username: string
  password: string
}

export type RegisterInput = {
  username: string
  email: string
  password: string
  role: RoleEnum
  first_name?: string
  last_name?: string
}

export type PendingApproval = {
  detail: string
  pending_approval: true
}