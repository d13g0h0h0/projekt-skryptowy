import json

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase

from .models import SubTask, Task

LIST_URL = "/api/tasks/"


def detail_url(pk):
    return f"/api/tasks/{pk}/"


class TaskApiTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="hanna", email="hanna@example.com", password="pass12345"
        )

    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type="application/json")

    def put_json(self, url, data):
        return self.client.put(url, data=json.dumps(data), content_type="application/json")

    def payload(self, **overrides):
        data = {"title": "Some title", "content": "Some task"}
        data.update(overrides)
        return data

    def make_task(self, title="Some title", content="Some task", subtasks=(), author=None):
        task = Task.objects.create(title=title, content=content, author=author or self.user)
        for position, s in enumerate(subtasks):
            SubTask.objects.create(task=task, content=s, position=position)
        return task


class CreateTaskTests(TaskApiTestCase):
    def test_create_task_without_subtasks(self):
        response = self.post_json(LIST_URL, self.payload(title="Simple", content="Simple task"))
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["title"], "Simple")
        self.assertEqual(body["content"], "Simple task")
        self.assertEqual(body["subtasks"], [])
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_sets_temporary_default_author(self):
        response = self.post_json(LIST_URL, self.payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.get().author.username, "dev")
        self.assertEqual(response.json()["author"]["username"], "dev")

    def test_create_reuses_default_author(self):
        self.post_json(LIST_URL, self.payload())
        self.post_json(LIST_URL, self.payload(title="Second"))
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(get_user_model().objects.filter(username="dev").count(), 1)

    def test_create_task_with_subtasks(self):
        response = self.post_json(
            LIST_URL,
            self.payload(subtasks=[{"content": "subtask 1"}, {"content": "subtask 2"}]),
        )
        self.assertEqual(response.status_code, 201)
        contents = [s["content"] for s in response.json()["subtasks"]]
        self.assertCountEqual(contents, ["subtask 1", "subtask 2"])
        self.assertEqual(SubTask.objects.count(), 2)

    def test_subtasks_positions_follow_input_order(self):
        response = self.post_json(
            LIST_URL,
            self.payload(subtasks=[{"content": "first"}, {"content": "second"}]),
        )
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get()
        ordered = list(task.subtasks.order_by("position").values_list("content", flat=True))
        self.assertEqual(ordered, ["first", "second"])

    def test_create_with_empty_subtasks_list(self):
        response = self.post_json(LIST_URL, self.payload(subtasks=[]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["subtasks"], [])

    def test_title_and_content_are_stripped(self):
        response = self.post_json(LIST_URL, self.payload(title="  title  ", content="  space  "))
        body = response.json()
        self.assertEqual(body["title"], "title")
        self.assertEqual(body["content"], "space")

    def test_create_with_invalid_data_returns_400(self):
        invalid = {
            "missing title": {"content": "x"},
            "empty title": self.payload(title=""),
            "too long title": self.payload(title="x" * 256),
            "missing content": {"title": "x"},
            "empty content": self.payload(content=""),
            "empty subtask": self.payload(subtasks=[{"content": ""}]),
            "too long subtask": self.payload(subtasks=[{"content": "x" * 256}]),
        }
        for name, data in invalid.items():
            with self.subTest(name):
                response = self.post_json(LIST_URL, data)
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_malformed_json_returns_400(self):
        response = self.client.post(LIST_URL, data="not a json", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class ListTaskTests(TaskApiTestCase):
    def test_list_empty(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_returns_summary_only(self):
        self.make_task(title="title", content="task", subtasks=["subtask"])
        data = self.client.get(LIST_URL).json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "title")
        self.assertEqual(data[0]["author"], {"id": self.user.pk, "username": "hanna"})
        self.assertIn("created_at", data[0])
        self.assertIn("updated_at", data[0])
        self.assertNotIn("content", data[0])
        self.assertNotIn("subtasks", data[0])

    def test_list_is_sorted_by_updated_at_desc(self):
        first = self.make_task(title="first")
        second = self.make_task(title="second")
        # wymuś nowszy updated_at dla pierwszego zadania
        first.title = "first (edited)"
        first.save()
        titles = [t["title"] for t in self.client.get(LIST_URL).json()]
        self.assertEqual(titles, ["first (edited)", "second"])

    def test_unsupported_method_returns_405(self):
        self.assertEqual(self.client.delete(LIST_URL).status_code, 405)


class DetailTaskTests(TaskApiTestCase):
    def test_get_task(self):
        task = self.make_task(title="title", content="task", subtasks=["subtask"])
        response = self.client.get(detail_url(task.pk))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["id"], task.pk)
        self.assertEqual(body["title"], "title")
        self.assertEqual(body["content"], "task")
        self.assertEqual(body["author"], {"id": self.user.pk, "username": "hanna"})
        self.assertEqual(body["subtasks"][0]["content"], "subtask")

    def test_get_returns_subtasks_ordered_by_position(self):
        task = self.make_task(subtasks=["a", "b", "c"])
        body = self.client.get(detail_url(task.pk)).json()
        self.assertEqual([s["content"] for s in body["subtasks"]], ["a", "b", "c"])

    def test_get_nonexistent_returns_404(self):
        self.assertEqual(self.client.get(detail_url(9999)).status_code, 404)


class UpdateTaskTests(TaskApiTestCase):
    def test_update_title_and_content(self):
        task = self.make_task(title="old title", content="old")
        response = self.put_json(detail_url(task.pk), self.payload(title="new title", content="new"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], "new title")
        self.assertEqual(body["content"], "new")
        task.refresh_from_db()
        self.assertEqual(task.title, "new title")
        self.assertEqual(task.content, "new")

    def test_update_does_not_change_author(self):
        other = get_user_model().objects.create_user(
            username="other", email="other@example.com", password="pass12345"
        )
        task = self.make_task(author=other)
        self.put_json(detail_url(task.pk), self.payload(content="x"))
        task.refresh_from_db()
        self.assertEqual(task.author, other)

    def test_update_without_subtasks_field_keeps_subtasks(self):
        task = self.make_task(subtasks=["a", "b"])
        self.put_json(detail_url(task.pk), self.payload(content="new"))
        self.assertEqual(task.subtasks.count(), 2)

    def test_update_with_subtasks_replaces_them(self):
        task = self.make_task(subtasks=["a", "b"])
        response = self.put_json(
            detail_url(task.pk), self.payload(subtasks=[{"content": "c"}])
        )
        self.assertEqual(response.status_code, 200)
        subtasks = list(task.subtasks.order_by("position"))
        self.assertEqual([s.content for s in subtasks], ["c"])
        self.assertEqual(subtasks[0].position, 0)

    def test_update_with_empty_list_removes_subtasks(self):
        task = self.make_task(subtasks=["a", "b"])
        self.put_json(detail_url(task.pk), self.payload(subtasks=[]))
        self.assertEqual(task.subtasks.count(), 0)

    def test_update_invalid_data_returns_400_and_changes_nothing(self):
        task = self.make_task(title="old title", content="old", subtasks=["a"])
        payloads = [
            self.payload(content=""),
            self.payload(title=""),
            {"content": "x"},
            self.payload(subtasks=[{"content": ""}]),
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.put_json(detail_url(task.pk), payload)
                self.assertEqual(response.status_code, 400)
        task.refresh_from_db()
        self.assertEqual(task.title, "old title")
        self.assertEqual(task.content, "old")
        self.assertEqual(task.subtasks.count(), 1)

    def test_update_nonexistent_returns_404(self):
        self.assertEqual(self.put_json(detail_url(9999), self.payload()).status_code, 404)


class DeleteTaskTests(TaskApiTestCase):
    def test_delete_task(self):
        task = self.make_task()
        response = self.client.delete(detail_url(task.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_cascades_to_subtasks(self):
        task = self.make_task(subtasks=["a", "b"])
        self.client.delete(detail_url(task.pk))
        self.assertEqual(SubTask.objects.count(), 0)

    def test_delete_nonexistent_returns_404(self):
        self.assertEqual(self.client.delete(detail_url(9999)).status_code, 404)


class ModelTests(TaskApiTestCase):
    def test_str_returns_title(self):
        self.assertEqual(str(self.make_task(title="My title")), "My title")

    def test_deleting_author_with_tasks_is_protected(self):
        self.make_task()
        with self.assertRaises(ProtectedError):
            self.user.delete()