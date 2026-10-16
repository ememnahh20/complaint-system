import unittest

from app import create_app
from config import Config


def make_client():
    cfg = Config(secret_key="t", admin_password="pw", sheet_id="", worksheet_name="",
                 credentials_file="", gmail_user="", gmail_app_password="", dev_mode=True)
    return create_app(cfg).test_client()


class AppTests(unittest.TestCase):
    def test_full_flow(self):
        c = make_client()
        for page in ("/", "/track", "/admin/login"):
            self.assertEqual(c.get(page).status_code, 200)

        r = c.post("/api/complaints", json=dict(name="Ana", email="a@b.com",
                   category="Academic", message="Mali ang grade ko sa Math"))
        self.assertEqual(r.status_code, 201)
        cid = r.get_json()["complaint_id"]

        self.assertEqual(c.post("/api/complaints", json={}).status_code, 400)
        self.assertEqual(c.get("/api/complaints/" + cid).get_json()["status"], "Pending")
        self.assertEqual(c.get("/api/complaints/NOPE").status_code, 404)

        self.assertEqual(c.get("/admin").status_code, 302)           # protected
        c.post("/admin/login", data={"password": "wrong"})
        self.assertEqual(c.get("/admin").status_code, 302)
        c.post("/admin/login", data={"password": "pw"})
        page = c.get("/admin")
        self.assertEqual(page.status_code, 200)
        self.assertIn(cid.encode(), page.data)

        c.post(f"/admin/complaints/{cid}/status", data={"status": "Resolved", "remarks": "Ayos na"})
        self.assertEqual(c.get("/api/complaints/" + cid).get_json()["status"], "Resolved")


if __name__ == "__main__":
    unittest.main()
