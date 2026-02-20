import pytest

from app.services.detection.intent import IntentDetector


class TestIntentDetector:
    def setup_method(self):
        self.detector = IntentDetector()

    def test_urgency_creation_detected(self):
        signals = self.detector.detect(
            "You must respond immediately. This is your final warning. Your account expires today."
        )
        assert any("urgency" in s.detail.lower() for s in signals)

    def test_authority_exploitation_detected(self):
        signals = self.detector.detect(
            "This is an official notice from the department of compliance. This is a mandatory legal communication."
        )
        assert any("authority" in s.detail.lower() for s in signals)

    def test_relationship_exploitation_detected(self):
        signals = self.detector.detect(
            "Hey grandma, I lost my phone and this is my new number. I'm in trouble and need help. Can you send money?"
        )
        assert any("relationship" in s.detail.lower() for s in signals)

    def test_unusual_action_gift_card(self):
        signals = self.detector.detect(
            "Please buy Steam gift cards and send the codes to this address"
        )
        assert any("unusual" in s.detail.lower() for s in signals)

    def test_info_harvesting_ssn(self):
        signals = self.detector.detect(
            "Please verify your social security number and date of birth to continue"
        )
        assert any("information" in s.detail.lower() or "harvesting" in s.detail.lower() for s in signals)

    def test_benign_message_no_intent(self):
        signals = self.detector.detect(
            "Would you like to grab coffee this afternoon?"
        )
        high_signals = [s for s in signals if s.score > 40]
        assert len(high_signals) == 0

    def test_multiple_intents_amplified(self):
        signals = self.detector.detect(
            "This is your final warning from the compliance department. "
            "You must act immediately or face legal action. "
            "Verify your social security number now. "
            "Send the payment via gift card."
        )
        assert any("multiple" in s.detail.lower() for s in signals)
