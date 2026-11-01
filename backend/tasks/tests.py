import json

from django.test import TestCase

from .models import SubTask, Task

LIST_URL = "/api/tasks/"


def detail_url(pk):
    return f"/api/tasks/{pk}/"


class TaskApiTestCase(TestCase):
    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type="application/json")

    def put_json(self, url, data):
        return self.client.put(url, data=json.dumps(data), content_type="application/json")

    def make_task(self, content="Some task", subtasks=()):
        task = Task.objects.create(content=content)
        for s in subtasks:
            SubTask.objects.create(task=task, content=s)
        return task


class CreateTaskTests(TaskApiTestCase):
    def test_create_task_without_subtasks(self):
        response = self.post_json(LIST_URL, {"content": "Simple task"})
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["content"], "Simple task")
        self.assertEqual(body["subtasks"], [])
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_with_subtasks(self):
        response = self.post_json(
            LIST_URL,
            {"content": "Task with subtasks", "subtasks": [{"content": "subtask 1"}, {"content": "subtask 2"}]},
        )
        self.assertEqual(response.status_code, 201)
        contents = [s["content"] for s in response.json()["subtasks"]]
        self.assertCountEqual(contents, ["subtask 1", "subtask 2"])
        self.assertEqual(SubTask.objects.count(), 2)

    def test_create_with_empty_subtasks_list(self):
        response = self.post_json(LIST_URL, {"content": "x", "subtasks": []})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["subtasks"], [])

    def test_content_is_stripped(self):
        response = self.post_json(LIST_URL, {"content": "  space  "})
        self.assertEqual(response.json()["content"], "space")

    def test_create_malformed_json_returns_400(self):
        response = self.client.post(LIST_URL, data="not a json", content_type="application/json")
        self.assertEqual(response.status_code, 400)


class ListTaskTests(TaskApiTestCase):
    def test_list_empty(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_returns_tasks_with_subtasks(self):
        self.make_task(content="task", subtasks=["subtask"])
        data = self.client.get(LIST_URL).json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["content"], "task")
        self.assertEqual(data[0]["subtasks"][0]["content"], "subtask")

    def test_unsupported_method_returns_405(self):
        self.assertEqual(self.client.delete(LIST_URL).status_code, 405)


class DetailTaskTests(TaskApiTestCase):
    def test_get_task(self):
        task = self.make_task(content="task", subtasks=["subtask"])
        response = self.client.get(detail_url(task.pk))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["id"], task.pk)
        self.assertEqual(body["content"], "task")
        self.assertEqual(body["subtasks"][0]["content"], "subtask")

    def test_get_nonexistent_returns_404(self):
        self.assertEqual(self.client.get(detail_url(9999)).status_code, 404)


class UpdateTaskTests(TaskApiTestCase):
    def test_update_content(self):
        task = self.make_task(content="old")
        response = self.put_json(detail_url(task.pk), {"content": "new"})
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.content, "new")

    def test_update_without_subtasks_field_keeps_subtasks(self):
        task = self.make_task(subtasks=["a", "b"])
        self.put_json(detail_url(task.pk), {"content": "new"})
        self.assertEqual(task.subtasks.count(), 2)

    def test_update_with_subtasks_replaces_them(self):
        task = self.make_task(subtasks=["a", "b"])
        response = self.put_json(
            detail_url(task.pk), {"content": "x", "subtasks": [{"content": "c"}]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([s.content for s in task.subtasks.all()], ["c"])

    def test_update_with_empty_list_removes_subtasks(self):
        task = self.make_task(subtasks=["a", "b"])
        self.put_json(detail_url(task.pk), {"content": "x", "subtasks": []})
        self.assertEqual(task.subtasks.count(), 0)

    def test_update_invalid_data_returns_400_and_changes_nothing(self):
        task = self.make_task(content="old", subtasks=["a"])
        for payload in [{"content": ""}, {"content": "x", "subtasks": [{"content": ""}]}]:
            with self.subTest(payload=payload):
                response = self.put_json(detail_url(task.pk), payload)
                self.assertEqual(response.status_code, 400)
        task.refresh_from_db()
        self.assertEqual(task.content, "old")
        self.assertEqual(task.subtasks.count(), 1)

    def test_update_nonexistent_returns_404(self):
        self.assertEqual(self.put_json(detail_url(9999), {"content": "x"}).status_code, 404)


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