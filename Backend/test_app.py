import unittest
from unittest.mock import patch

import app as chatbot_app


class ChatbotApiTests(unittest.TestCase):
    def setUp(self):
        chatbot_app.app.config.update(TESTING=True)
        self.client = chatbot_app.app.test_client()
        chatbot_app._conversations.clear()
        chatbot_app._rate_limit_store.clear()

    def start_conversation(self):
        response = self.client.get("/start")
        self.assertEqual(response.status_code, 200)
        conversation_id = response.get_json()["thread_id"]
        self.assertTrue(conversation_id)
        return conversation_id

    def test_health_check_reports_responses_api(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["api"], "responses")

    def test_start_creates_local_conversation(self):
        conversation_id = self.start_conversation()
        self.assertIn(conversation_id, chatbot_app._conversations)

    def test_chat_requires_valid_json(self):
        response = self.client.post("/chat", data="not-json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertIn("valid JSON", response.get_json()["error"])

    def test_chat_requires_conversation_id(self):
        response = self.client.post("/chat", json={"message": "Hello"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Missing thread_id")

    def test_chat_rejects_unknown_conversation(self):
        response = self.client.post(
            "/chat", json={"thread_id": "not-real", "message": "Hello"}
        )
        self.assertEqual(response.status_code, 404)

    def test_chat_rejects_oversized_message(self):
        conversation_id = self.start_conversation()
        response = self.client.post(
            "/chat",
            json={"thread_id": conversation_id, "message": "x" * 501},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Message too long", response.get_json()["error"])

    @patch("app.functions.create_response", return_value="Hello from Water Warehouse")
    def test_chat_saves_bounded_conversation_history(self, create_response):
        conversation_id = self.start_conversation()
        response = self.client.post(
            "/chat",
            json={"thread_id": conversation_id, "message": "Hello"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["response"], "Hello from Water Warehouse")
        create_response.assert_called_once()
        sent_history = create_response.call_args.args[1]
        self.assertEqual(sent_history, [{"role": "user", "content": "Hello"}])
        self.assertEqual(
            chatbot_app._conversations[conversation_id]["messages"],
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hello from Water Warehouse"},
            ],
        )

    @patch("app.functions.create_response", side_effect=RuntimeError("upstream failed"))
    def test_chat_returns_safe_upstream_error(self, _create_response):
        conversation_id = self.start_conversation()
        response = self.client.post(
            "/chat",
            json={"thread_id": conversation_id, "message": "Hello"},
        )
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("upstream failed", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
