from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

LOGIN = "/api/auth/login/"
LOGOUT = "/api/auth/logout/"
ME = "/api/auth/me/"
REGISTER = "/api/auth/register/"

PASSWORD = "Silne-haslo-123"


class RegisterTests(APITestCase):
    payload = {
        "username": "anna",
        "email": "anna@example.com",
        "password": PASSWORD,
        "first_name": "Anna",
        "last_name": "Kowalska",
    }

    def test_register_creates_student_and_hashes_password(self):
        r = self.client.post(REGISTER, self.payload, format="json")
        self.assertEqual(r.status_code, 201)
        user = User.objects.get(username="anna")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotIn("password", r.data)

    def test_register_saves_first_and_last_name(self):
        r = self.client.post(REGISTER, self.payload, format="json")
        self.assertEqual(r.status_code, 201)
        user = User.objects.get(username="anna")
        self.assertEqual(user.first_name, "Anna")
        self.assertEqual(user.last_name, "Kowalska")
        self.assertEqual(r.data["first_name"], "Anna")
        self.assertEqual(r.data["last_name"], "Kowalska")

    def test_names_are_optional(self):
        data = {k: v for k, v in self.payload.items() if k not in ("first_name", "last_name")}
        r = self.client.post(REGISTER, data, format="json")
        self.assertEqual(r.status_code, 201)
        user = User.objects.get(username="anna")
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")

    def test_register_logs_user_in(self):
        self.client.post(REGISTER, self.payload, format="json")
        self.assertEqual(self.client.get(ME).status_code, 200)

    def test_cannot_set_role_or_staff_flags(self):
        data = {**self.payload, "role": "teacher", "is_staff": True, "is_superuser": True}
        self.client.post(REGISTER, data, format="json")
        user = User.objects.get(username="anna")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicate_username_rejected(self):
        self.client.post(REGISTER, self.payload, format="json")
        r = self.client.post(
            REGISTER, {**self.payload, "email": "inny@example.com"}, format="json"
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email_rejected(self):
        self.client.post(REGISTER, self.payload, format="json")
        r = self.client.post(
            REGISTER, {**self.payload, "username": "inna"}, format="json"
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_weak_password_rejected(self):
        r = self.client.post(REGISTER, {**self.payload, "password": "123"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.exists())

    def test_missing_required_fields(self):
        r = self.client.post(REGISTER, {"username": "anna"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("email", r.data)
        self.assertIn("password", r.data)


class SessionAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="piotr",
            email="piotr@example.com",
            password=PASSWORD,
            first_name="Piotr",
            last_name="Nowak",
        )

    def test_login_ok(self):
        r = self.client.post(LOGIN, {"username": "piotr", "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "piotr")
        self.assertEqual(r.data["role"], "student")
        self.assertEqual(r.data["first_name"], "Piotr")
        self.assertEqual(r.data["last_name"], "Nowak")

    def test_login_wrong_password(self):
        r = self.client.post(LOGIN, {"username": "piotr", "password": "zle"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_login_missing_fields(self):
        r = self.client.post(LOGIN, {"username": "piotr"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_me_requires_login(self):
        self.assertIn(self.client.get(ME).status_code, (401, 403))

    def test_me_returns_current_user(self):
        self.client.force_login(self.user)
        r = self.client.get(ME)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["id"], self.user.id)
        self.assertEqual(r.data["first_name"], "Piotr")
        self.assertEqual(r.data["last_name"], "Nowak")
        self.assertIn("scopes", r.data)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(LOGOUT).status_code, 204)
        self.assertIn(self.client.get(ME).status_code, (401, 403))


class UserModelTests(APITestCase):
    def test_is_teacher(self):
        t = User.objects.create_user(
            username="t", email="t@example.com", password="x", role=User.Role.TEACHER
        )
        s = User.objects.create_user(username="s", email="s@example.com", password="x")
        self.assertTrue(t.is_teacher)
        self.assertFalse(s.is_teacher)