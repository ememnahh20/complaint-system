import unittest

from models.complaint import Status
from repositories.memory_repository import InMemoryComplaintRepository
from services.complaint_service import (ComplaintNotFound, ComplaintService,
                                        ValidationError)
from services.email_service import ComplaintNotifier, EmailSender


class FakeSender(EmailSender):
    def __init__(self, fail=False):
        self.sent, self.fail = [], fail

    def send(self, to, subject, html_body):
        if self.fail:
            raise RuntimeError("smtp down")
        self.sent.append((to, subject, html_body))


def make(fail=False):
    sender = FakeSender(fail)
    return ComplaintService(InMemoryComplaintRepository(), ComplaintNotifier(sender)), sender


VALID = dict(name="Juan Dela Cruz", email="juan@school.edu",
             category="Facilities", message="Sira ang aircon sa Room 204")


class ServiceTests(unittest.TestCase):
    def test_submit_sends_email_with_id(self):
        svc, sender = make()
        result = svc.submit(**VALID)
        self.assertTrue(result["email_sent"])
        self.assertIn(result["complaint_id"], sender.sent[0][2])
        self.assertEqual(sender.sent[0][0], "juan@school.edu")

    def test_ids_are_unique_and_formatted(self):
        svc, _ = make()
        a, b = svc.submit(**VALID)["complaint_id"], svc.submit(**VALID)["complaint_id"]
        self.assertNotEqual(a, b)
        self.assertRegex(a, r"^CMP-\d{4}-0001-[A-Z0-9]{4}$")

    def test_validation(self):
        svc, _ = make()
        for bad in ({"email": "nope"}, {"name": ""}, {"category": "X"}, {"message": "short"}):
            with self.assertRaises(ValidationError):
                svc.submit(**{**VALID, **bad})

    def test_email_failure_keeps_complaint(self):
        svc, _ = make(fail=True)
        result = svc.submit(**VALID)
        self.assertFalse(result["email_sent"])
        self.assertEqual(svc.track(result["complaint_id"])["status"], "Pending")

    def test_track_hides_private_data_and_is_case_insensitive(self):
        svc, _ = make()
        cid = svc.submit(**VALID)["complaint_id"]
        info = svc.track(cid.lower())
        self.assertNotIn("email", info)
        self.assertNotIn("message", info)

    def test_track_unknown(self):
        svc, _ = make()
        with self.assertRaises(ComplaintNotFound):
            svc.track("CMP-0000")

    def test_resolve_sends_email_once(self):
        svc, sender = make()
        cid = svc.submit(**VALID)["complaint_id"]
        svc.update_status(cid, "Resolved", "Napalitan na ang aircon")
        svc.update_status(cid, "Resolved")
        resolved = [m for m in sender.sent if m[1].startswith("Complaint Resolved")]
        self.assertEqual(len(resolved), 1)
        self.assertIn("Napalitan", resolved[0][2])
        self.assertEqual(svc.track(cid)["status"], "Resolved")

    def test_in_progress_sends_no_resolved_email(self):
        svc, sender = make()
        cid = svc.submit(**VALID)["complaint_id"]
        svc.update_status(cid, "In Progress")
        self.assertEqual(len(sender.sent), 1)

    def test_invalid_status(self):
        svc, _ = make()
        cid = svc.submit(**VALID)["complaint_id"]
        with self.assertRaises(ValidationError):
            svc.update_status(cid, "Done")

    def test_list_filter_and_stats(self):
        svc, _ = make()
        a = svc.submit(**VALID)["complaint_id"]
        svc.submit(**VALID)
        svc.update_status(a, "Resolved")
        self.assertEqual(len(svc.list_complaints("Resolved")), 1)
        self.assertEqual(svc.stats(), {"total": 2, "Pending": 1, "In Progress": 0, "Resolved": 1})

    def test_row_roundtrip(self):
        from models.complaint import Complaint
        svc, _ = make()
        cid = svc.submit(**VALID)["complaint_id"]
        svc.update_status(cid, "Resolved", "ok")
        c = svc._repo.get(cid)
        rebuilt = Complaint.from_record(dict(zip(Complaint.HEADERS, c.to_row())))
        self.assertEqual(rebuilt.to_row(), c.to_row())


if __name__ == "__main__":
    unittest.main()
