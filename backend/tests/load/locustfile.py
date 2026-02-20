"""Load test configuration targeting 10,000 concurrent users.

Run: locust -f tests/load/locustfile.py --host http://localhost:8880
Target: p95 < 3 seconds for all scan endpoints
"""

from locust import HttpUser, between, task


class ScanUser(HttpUser):
    wait_time = between(1, 3)
    headers = {"X-API-Key": "load-test-key", "Content-Type": "application/json"}

    @task(5)
    def scan_text(self):
        self.client.post(
            "/v1/scan",
            json={
                "content": "URGENT: Your account has been suspended. Click here to verify.",
                "scan_type": "text",
            },
            headers=self.headers,
        )

    @task(3)
    def scan_url(self):
        self.client.post(
            "/v1/scan",
            json={
                "content": "https://example-phishing.xyz/login",
                "scan_type": "url",
            },
            headers=self.headers,
        )

    @task(1)
    def scan_safe_url(self):
        self.client.post(
            "/v1/scan",
            json={
                "content": "https://www.google.com",
                "scan_type": "url",
            },
            headers=self.headers,
        )

    @task(2)
    def get_recovery_checklist(self):
        self.client.get(
            "/v1/recovery/checklist/credential_theft",
            headers=self.headers,
        )

    @task(1)
    def triage_recovery(self):
        self.client.post(
            "/v1/recovery/triage",
            json={
                "answers": [
                    {"question_id": "q1", "selected_option_id": "q1_password"},
                ],
            },
            headers=self.headers,
        )

    @task(1)
    def health_check(self):
        self.client.get("/v1/health")

    @task(1)
    def submit_feedback(self):
        self.client.post(
            "/v1/feedback",
            json={
                "scan_id": "load-test-scan",
                "user_verdict": "correct",
            },
            headers=self.headers,
        )
