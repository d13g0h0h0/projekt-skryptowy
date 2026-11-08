from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.tasks.models import Task,SubTask
from apps.tasks.views import get_default_author

from .models import Solution, SolutionPart, Vote

User = get_user_model()
JSON = "application/json"


class SolutionsTestCase(TestCase):

    def setUp(self):
        self.user = get_default_author()  # the user the views act as for now ("dev")
        self.other = User.objects.create_user("ola", email="ola@example.com", password="x")
        self.third = User.objects.create_user("ewa", email="ewa@example.com", password="x")

        self.task = Task.objects.create(title="Task", content="How much is 2+2", author=self.user)
        self.sub1 = SubTask.objects.create(task=self.task, content="How about 3+3?", position=0)
        self.sub2 = SubTask.objects.create(task=self.task, content="How about 4+4?", position=1)

        self.plain_task = Task.objects.create(title="Plain", content="How much is 1+1?", author=self.user)

    # --- urls ---
    def solutions_url(self, task=None):
        return f"/api/tasks/{(task or self.task).pk}/solutions/"

    def solution_url(self, pk):
        return f"/api/solutions/{pk}/"

    def vote_url(self, pk):
        return f"/api/solutions/{pk}/vote/"

    def valid_payload(self):
        return {
            "content": "2+2=4",
            "parts": [
                {"subtask_id": self.sub1.pk, "content": "3+3=6"},
                {"subtask_id": self.sub2.pk, "content": "4+4=8"},
            ],
        }

    def make_solution(self, author=None, task=None, content="2+2=4"):
        task = task or self.task
        solution = Solution.objects.create(
            task=task, author=author or self.user, content=content
        )
        for subtask in task.subtasks.all():
            SolutionPart.objects.create(
                solution=solution, subtask=subtask, content=f"answer {subtask.pk}"
            )
        return solution

    def post_solution(self, payload, task=None):
        return self.client.post(self.solutions_url(task), payload, content_type=JSON)

    def put_solution(self, pk, payload):
        return self.client.put(self.solution_url(pk), payload, content_type=JSON)

    def put_vote(self, pk, payload):
        return self.client.put(self.vote_url(pk), payload, content_type=JSON)

class SolutionCreateTests(SolutionsTestCase):
    def test_create_with_all_parts(self):
        response = self.post_solution(self.valid_payload())

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["content"], "2+2=4")
        self.assertEqual(body["author"], {"id": self.user.id, "username": "dev"})
        self.assertEqual(body["score"], 0)
        self.assertIsNone(body["my_vote"])
        self.assertEqual(
            {(p["subtask_id"], p["content"]) for p in body["parts"]},
            {(self.sub1.pk, "3+3=6"), (self.sub2.pk, "4+4=8")},
        )
        self.assertEqual(Solution.objects.count(), 1)
        self.assertEqual(SolutionPart.objects.count(), 2)
        self.assertEqual(Solution.objects.get().task, self.task)

    def test_content_is_optional_when_task_has_subtasks(self):
        payload = self.valid_payload()
        del payload["content"]

        response = self.post_solution(payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["content"], "")

    def test_whitespace_is_stripped(self):
        payload = self.valid_payload()
        payload["content"] = "  2+2=4  "
        payload["parts"][0]["content"] = "  3+3=6 "

        body = self.post_solution(payload).json()

        self.assertEqual(body["content"], "2+2=4")
        self.assertIn("3+3=6", [p["content"] for p in body["parts"]])

    def test_parts_are_required_when_task_has_subtasks(self):
        response = self.post_solution({"content": "2+2=4"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Solution.objects.count(), 0)

    def test_empty_parts_list_is_rejected(self):
        response = self.post_solution({"content": "2+2=4", "parts": []})

        self.assertEqual(response.status_code, 400)

    def test_missing_one_subtask_is_rejected(self):
        payload = self.valid_payload()
        payload["parts"].pop()  # only sub1 answered

        response = self.post_solution(payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Solution.objects.count(), 0)
        self.assertEqual(SolutionPart.objects.count(), 0)

    def test_subtask_of_another_task_is_rejected(self):
        foreign = SubTask.objects.create(task=self.plain_task, content="x", position=0)
        payload = self.valid_payload()
        payload["parts"][1]["subtask_id"] = foreign.pk  # replaces sub2

        self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_extra_subtask_is_rejected(self):
        foreign = SubTask.objects.create(task=self.plain_task, content="x", position=0)
        payload = self.valid_payload()
        payload["parts"].append({"subtask_id": foreign.pk, "content": "extra"})

        self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_unknown_subtask_is_rejected(self):
        payload = self.valid_payload()
        payload["parts"][1]["subtask_id"] = 999999

        self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_duplicate_subtask_is_rejected(self):
        payload = self.valid_payload()
        payload["parts"].append({"subtask_id": self.sub1.pk, "content": "again"})

        self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_empty_part_content_is_rejected(self):
        for bad in ["", "   "]:
            with self.subTest(content=bad):
                payload = self.valid_payload()
                payload["parts"][0]["content"] = bad
                self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_non_integer_subtask_id_is_rejected(self):
        for bad in [str(self.sub1.pk), True, None, 1.5]:
            with self.subTest(subtask_id=bad):
                payload = self.valid_payload()
                payload["parts"][0]["subtask_id"] = bad
                self.assertEqual(self.post_solution(payload).status_code, 400)

    def test_malformed_bodies_are_rejected(self):
        bad_bodies = [
            "not json",
            "[]",
            "null",
            {"content": 5, "parts": []},
            {"parts": "abc"},
            {"parts": [{"subtask_id": self.sub1.pk}]},                    # no content
            {"parts": [{"subtask_id": self.sub1.pk, "content": 5}]},      # content not a string
            {"parts": [{"content": "x"}]},                                # no subtask_id
        ]
        for body in bad_bodies:
            with self.subTest(body=body):
                response = self.post_solution(body)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Solution.objects.count(), 0)

    def test_task_without_subtasks_accepts_content_only(self):
        response = self.post_solution({"content": "2"}, task=self.plain_task)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["parts"], [])

    def test_task_without_subtasks_requires_content(self):
        for body in [{}, {"content": ""}, {"content": "   "}]:
            with self.subTest(body=body):
                self.assertEqual(self.post_solution(body, task=self.plain_task).status_code, 400)

    def test_task_without_subtasks_rejects_parts(self):
        foreign = self.sub1  # a real subtask, but of another task
        payload = {"content": "2", "parts": [{"subtask_id": foreign.pk, "content": "x"}]}

        self.assertEqual(self.post_solution(payload, task=self.plain_task).status_code, 400)

    def test_unknown_task_returns_404(self):
        response = self.client.post(
            "/api/tasks/999999/solutions/", self.valid_payload(), content_type=JSON
        )

        self.assertEqual(response.status_code, 404)

class SolutionListTests(SolutionsTestCase):
    def test_empty_list(self):
        response = self.client.get(self.solutions_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_unknown_task_returns_404(self):
        self.assertEqual(self.client.get("/api/tasks/999999/solutions/").status_code, 404)

    def test_returns_full_solutions_with_parts(self):
        solution = self.make_solution(content="2+2=4")

        body = self.client.get(self.solutions_url()).json()

        self.assertEqual(len(body), 1)
        item = body[0]
        self.assertEqual(item["id"], solution.pk)
        self.assertEqual(item["content"], "2+2=4")
        self.assertEqual(item["author"], {"id": self.user.id, "username": "dev"})
        self.assertEqual(len(item["parts"]), 2)
        self.assertEqual(
            {p["subtask_id"] for p in item["parts"]}, {self.sub1.pk, self.sub2.pk}
        )
        for key in ("score", "my_vote", "created_at", "updated_at"):
            self.assertIn(key, item)

    def test_only_solutions_of_this_task(self):
        mine = self.make_solution()
        self.make_solution(task=self.plain_task, content="other task")

        body = self.client.get(self.solutions_url()).json()

        self.assertEqual([s["id"] for s in body], [mine.pk])

    def test_sorted_by_score_then_newest(self):
        now = timezone.now()
        oldest = self.make_solution(content="oldest")
        newer = self.make_solution(content="newer")
        best = self.make_solution(content="best")
        # set timestamps explicitly - two creations can share a timestamp on some systems
        Solution.objects.filter(pk=oldest.pk).update(created_at=now - timedelta(hours=3))
        Solution.objects.filter(pk=newer.pk).update(created_at=now - timedelta(hours=2))
        Solution.objects.filter(pk=best.pk).update(created_at=now - timedelta(hours=4))
        Vote.objects.create(user=self.other, solution=best, value=Vote.Value.UP)

        body = self.client.get(self.solutions_url()).json()

        # best (score 1) first, then equal scores: newer before oldest
        self.assertEqual([s["id"] for s in body], [best.pk, newer.pk, oldest.pk])

    def test_score_is_sum_of_votes(self):
        solution = self.make_solution()
        Vote.objects.create(user=self.user, solution=solution, value=Vote.Value.DOWN)
        Vote.objects.create(user=self.other, solution=solution, value=Vote.Value.UP)
        Vote.objects.create(user=self.third, solution=solution, value=Vote.Value.UP)

        body = self.client.get(self.solutions_url()).json()

        self.assertEqual(body[0]["score"], 1)

    def test_negative_score(self):
        solution = self.make_solution()
        Vote.objects.create(user=self.other, solution=solution, value=Vote.Value.DOWN)
        Vote.objects.create(user=self.third, solution=solution, value=Vote.Value.DOWN)

        self.assertEqual(self.client.get(self.solutions_url()).json()[0]["score"], -2)

    def test_my_vote_is_per_current_user(self):
        upvoted = self.make_solution(content="up")
        downvoted = self.make_solution(content="down")
        voted_by_other = self.make_solution(content="other")
        not_voted = self.make_solution(content="none")
        Vote.objects.create(user=self.user, solution=upvoted, value=Vote.Value.UP)
        Vote.objects.create(user=self.user, solution=downvoted, value=Vote.Value.DOWN)
        Vote.objects.create(user=self.other, solution=voted_by_other, value=Vote.Value.UP)

        body = self.client.get(self.solutions_url()).json()
        my_vote = {s["id"]: s["my_vote"] for s in body}

        self.assertEqual(my_vote[upvoted.pk], 1)
        self.assertEqual(my_vote[downvoted.pk], -1)
        self.assertIsNone(my_vote[voted_by_other.pk])
        self.assertIsNone(my_vote[not_voted.pk])

class SolutionDetailTests(SolutionsTestCase):

    def test_put_replaces_content_and_parts(self):
        solution = self.make_solution()
        payload = {
            "content": "new content",
            "parts": [
                {"subtask_id": self.sub1.pk, "content": "new 1"},
                {"subtask_id": self.sub2.pk, "content": "new 2"},
            ],
        }

        response = self.put_solution(solution.pk, payload)

        self.assertEqual(response.status_code, 200)
        solution.refresh_from_db()
        self.assertEqual(solution.content, "new content")
        self.assertEqual(
            {p.subtask_id: p.content for p in solution.parts.all()},
            {self.sub1.pk: "new 1", self.sub2.pk: "new 2"},
        )
        self.assertEqual(SolutionPart.objects.count(), 2)  # old ones are gone, not duplicated
        self.assertEqual(response.json()["content"], "new content")

    def test_put_incomplete_parts_is_rejected_and_changes_nothing(self):
        solution = self.make_solution(content="original")
        payload = {"content": "new", "parts": [{"subtask_id": self.sub1.pk, "content": "x"}]}

        response = self.put_solution(solution.pk, payload)

        self.assertEqual(response.status_code, 400)
        solution.refresh_from_db()
        self.assertEqual(solution.content, "original")
        self.assertEqual(solution.parts.count(), 2)

    def test_put_without_parts_is_rejected_for_task_with_subtasks(self):
        solution = self.make_solution()

        self.assertEqual(self.put_solution(solution.pk, {"content": "new"}).status_code, 400)

    def test_put_keeps_score_and_my_vote(self):
        solution = self.make_solution()
        Vote.objects.create(user=self.user, solution=solution, value=Vote.Value.UP)
        Vote.objects.create(user=self.other, solution=solution, value=Vote.Value.UP)

        body = self.put_solution(solution.pk, self.valid_payload()).json()

        self.assertEqual(body["score"], 2)
        self.assertEqual(body["my_vote"], 1)

    def test_put_on_task_without_subtasks(self):
        solution = self.make_solution(task=self.plain_task, content="old")

        ok = self.put_solution(solution.pk, {"content": "new"})
        empty = self.put_solution(solution.pk, {"content": ""})

        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.json()["content"], "new")
        self.assertEqual(empty.status_code, 400)

    def test_put_unknown_solution_returns_404(self):
        self.assertEqual(self.put_solution(999999, self.valid_payload()).status_code, 404)

    def test_delete_removes_solution_with_parts_and_votes(self):
        solution = self.make_solution()
        Vote.objects.create(user=self.other, solution=solution, value=Vote.Value.UP)

        response = self.client.delete(self.solution_url(solution.pk))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Solution.objects.count(), 0)
        self.assertEqual(SolutionPart.objects.count(), 0)
        self.assertEqual(Vote.objects.count(), 0)

    def test_delete_unknown_solution_returns_404(self):
        self.assertEqual(self.client.delete(self.solution_url(999999)).status_code, 404)

class VoteTests(SolutionsTestCase):
    def setUp(self):
        super().setUp()
        self.solution = self.make_solution(author=self.other)

    def test_first_vote_creates(self):
        response = self.put_vote(self.solution.pk, {"value": 1})

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["value"], 1)
        self.assertEqual(body["user"], {"id": self.user.id, "username": "dev"})
        vote = Vote.objects.get()
        self.assertEqual((vote.user, vote.solution, vote.value), (self.user, self.solution, 1))

    def test_vote_again_changes_value_instead_of_duplicating(self):
        self.put_vote(self.solution.pk, {"value": 1})

        response = self.put_vote(self.solution.pk, {"value": -1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().value, -1)

    def test_same_value_twice_is_idempotent(self):
        self.put_vote(self.solution.pk, {"value": 1})

        response = self.put_vote(self.solution.pk, {"value": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.count(), 1)

    def test_does_not_touch_votes_of_other_users(self):
        Vote.objects.create(user=self.other, solution=self.solution, value=Vote.Value.UP)

        self.put_vote(self.solution.pk, {"value": -1})

        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(Vote.objects.get(user=self.other).value, 1)

    def test_invalid_values_are_rejected(self):
        for bad in [0, 2, -2, "1", True, None, {}]:
            with self.subTest(value=bad):
                response = self.put_vote(self.solution.pk, {"value": bad})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Vote.objects.count(), 0)

    def test_missing_value_and_malformed_body_are_rejected(self):
        for body in [{}, "not json", "[]", "null"]:
            with self.subTest(body=body):
                self.assertEqual(self.put_vote(self.solution.pk, body).status_code, 400)

    def test_vote_on_unknown_solution_returns_404(self):
        self.assertEqual(self.put_vote(999999, {"value": 1}).status_code, 404)

    def test_delete_removes_only_my_vote(self):
        Vote.objects.create(user=self.user, solution=self.solution, value=Vote.Value.UP)
        Vote.objects.create(user=self.other, solution=self.solution, value=Vote.Value.UP)

        response = self.client.delete(self.vote_url(self.solution.pk))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().user, self.other)

    def test_delete_without_vote_returns_404(self):
        self.assertEqual(self.client.delete(self.vote_url(self.solution.pk)).status_code, 404)

    def test_vote_is_reflected_in_solution_list(self):
        def listed():
            return self.client.get(self.solutions_url()).json()[0]

        self.assertIsNone(listed()["my_vote"])
        self.assertEqual(listed()["score"], 0)

        self.put_vote(self.solution.pk, {"value": 1})
        self.assertEqual(listed()["my_vote"], 1)
        self.assertEqual(listed()["score"], 1)

        self.put_vote(self.solution.pk, {"value": -1})
        self.assertEqual(listed()["my_vote"], -1)
        self.assertEqual(listed()["score"], -1)

        self.client.delete(self.vote_url(self.solution.pk))
        self.assertIsNone(listed()["my_vote"])
        self.assertEqual(listed()["score"], 0)