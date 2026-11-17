import { request } from "./client.ts";
import type { CreateSolutionInput, CreateVoteInput, Solution, SolutionId, Vote} from "./types.ts";

const endpoint = "/api/solutions/";

export const solutionsApi = {
  update: (id: SolutionId, input: CreateSolutionInput) =>
    request<Solution>(`${endpoint}${id}`, { method: 'PUT', body: input }),
  remove: (id: SolutionId) =>
    request<void>(`${endpoint}${id}`, { method: 'DELETE' }),
  update_vote: (id: SolutionId, input: CreateVoteInput) =>
    request<Vote>(`${endpoint}${id}/vote/`, { method: 'PUT', body: input }),
  remove_vote: (id: SolutionId) =>
    request<void>(`${endpoint}${id}/vote/`, { method: 'DELETE' }),
}