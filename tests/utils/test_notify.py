"""Tests for notification utilities in utils/notify.py."""

from unittest.mock import MagicMock, patch

import pytest

from praxis.backend.utils.notify import CELLPHONE_CARRIER_GATEWAYS, Notifier


class TestCellphoneCarrierGateways:

    """Tests for CELLPHONE_CARRIER_GATEWAYS constant."""

    def test_carrier_gateways_is_dict(self) -> None:
        """Test that CELLPHONE_CARRIER_GATEWAYS is a dictionary."""
        assert isinstance(CELLPHONE_CARRIER_GATEWAYS, dict)

    def test_carrier_gateways_has_major_carriers(self) -> None:
        """Test that major carriers are present in the gateways dict."""
        major_carriers = ["att", "verizon", "tmobile", "sprint"]
        for carrier in major_carriers:
            assert carrier in CELLPHONE_CARRIER_GATEWAYS

    def test_carrier_gateways_values_are_email_domains(self) -> None:
        """Test that all gateway values start with @ symbol."""
        for gateway in CELLPHONE_CARRIER_GATEWAYS.values():
            assert gateway.startswith("@")

    def test_specific_carrier_gateway(self) -> None:
        """Test specific carrier gateway mappings."""
        assert CELLPHONE_CARRIER_GATEWAYS["att"] == "@txt.att.net"
        assert CELLPHONE_CARRIER_GATEWAYS["verizon"] == "@vtext.com"
        assert CELLPHONE_CARRIER_GATEWAYS["tmobile"] == "@tmomail.net"


class TestNotifierInit:

    """Tests for Notifier initialization."""

    def test_can_instantiate_notifier(self) -> None:
        """Test that Notifier can be instantiated."""
        notifier = Notifier(
            smtp_server="smtp.example.com",
            smtp_port=587,
            smtp_username="user@example.com",
            smtp_password="password123",
        )
        assert notifier is not None

    def test_notifier_stores_smtp_server(self) -> None:
        """Test that Notifier stores SMTP server configuration."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="test@test.com",
            smtp_password="pass",
        )
        assert notifier.smtp_server == "smtp.test.com"
        assert notifier.smtp_port == 587
        assert notifier.smtp_username == "test@test.com"
        assert notifier.smtp_password == "pass"


class TestNotifierSendEmail:

    """Tests for Notifier.send_email method."""

    @patch("praxis.backend.utils.notify.smtplib.SMTP")
    def test_send_email_creates_smtp_connection(self, mock_smtp: MagicMock) -> None:
        """Test that send_email creates SMTP connection."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_email(
            sender_email="sender@test.com",
            recipient_email="recipient@test.com",
            subject="Test Subject",
            body="Test Body",
        )

        mock_smtp.assert_called_once_with("smtp.test.com", 587)

    @patch("praxis.backend.utils.notify.smtplib.SMTP")
    def test_send_email_logs_in_to_smtp(self, mock_smtp: MagicMock) -> None:
        """Test that send_email logs in to SMTP server."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="testuser",
            smtp_password="testpass",
        )

        notifier.send_email(
            sender_email="sender@test.com",
            recipient_email="recipient@test.com",
            subject="Test",
            body="Body",
        )

        mock_server.login.assert_called_once_with("testuser", "testpass")

    @patch("praxis.backend.utils.notify.smtplib.SMTP")
    def test_send_email_sends_message(self, mock_smtp: MagicMock) -> None:
        """Test that send_email sends the message."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_email(
            sender_email="sender@test.com",
            recipient_email="recipient@test.com",
            subject="Test Subject",
            body="Test Body",
        )

        mock_server.send_message.assert_called_once()

    @patch("praxis.backend.utils.notify.smtplib.SMTP")
    def test_send_email_constructs_message_correctly(
        self, mock_smtp: MagicMock,
    ) -> None:
        """Test that email message is constructed with correct fields."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_email(
            sender_email="alice@test.com",
            recipient_email="bob@test.com",
            subject="Important Message",
            body="Hello Bob",
        )

        # Check that send_message was called with a message object
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]

        assert message["From"] == "alice@test.com"
        assert message["To"] == "bob@test.com"
        assert message["Subject"] == "Important Message"

    @patch("praxis.backend.utils.notify.smtplib.SMTP")
    def test_send_email_handles_exception_silently(self, mock_smtp: MagicMock) -> None:
        """Test that send_email handles exceptions without raising."""
        mock_smtp.side_effect = Exception("SMTP connection failed")

        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        # Should not raise exception
        notifier.send_email(
            sender_email="sender@test.com",
            recipient_email="recipient@test.com",
            subject="Test",
            body="Body",
        )


class TestNotifierSendText:

    """Tests for Notifier.send_text method."""

    @patch.object(Notifier, "send_email")
    def test_send_text_calls_send_email(self, mock_send_email: MagicMock) -> None:
        """Test that send_text calls send_email internally."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_text(
            sender_email="sender@test.com",
            recipient_phone="5551234567",
            carrier="att",
            subject="Test SMS",
            body="Hello via SMS",
        )

        mock_send_email.assert_called_once()

    @patch.object(Notifier, "send_email")
    def test_send_text_constructs_carrier_email(
        self, mock_send_email: MagicMock,
    ) -> None:
        """Test that send_text constructs correct carrier email address."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_text(
            sender_email="sender@test.com",
            recipient_phone="5551234567",
            carrier="att",
            subject="Test",
            body="Body",
        )

        # Check that send_email was called with correct carrier gateway
        # send_email is called with positional args: (sender, recipient, subject, body)
        call_args = mock_send_email.call_args
        recipient_email = call_args[0][1]  # Second positional arg
        assert recipient_email == "5551234567@txt.att.net"

    @patch.object(Notifier, "send_email")
    def test_send_text_with_different_carriers(
        self, mock_send_email: MagicMock,
    ) -> None:
        """Test send_text with different carrier gateways."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        carriers_and_gateways = [
            ("verizon", "@vtext.com"),
            ("tmobile", "@tmomail.net"),
            ("sprint", "@messaging.sprintpcs.com"),
        ]

        for carrier, expected_gateway in carriers_and_gateways:
            mock_send_email.reset_mock()

            notifier.send_text(
                sender_email="sender@test.com",
                recipient_phone="5551234567",
                carrier=carrier,
                subject="Test",
                body="Body",
            )

            call_args = mock_send_email.call_args
            recipient_email = call_args[0][1]  # Second positional arg
            assert recipient_email == f"5551234567{expected_gateway}"

    @patch.object(Notifier, "send_email")
    def test_send_text_forwards_all_parameters(
        self, mock_send_email: MagicMock,
    ) -> None:
        """Test that send_text forwards all parameters to send_email."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        notifier.send_text(
            sender_email="alice@test.com",
            recipient_phone="5559876543",
            carrier="att",
            subject="Important SMS",
            body="Hello from email-to-SMS",
        )

        mock_send_email.assert_called_once_with(
            "alice@test.com",
            "5559876543@txt.att.net",
            "Important SMS",
            "Hello from email-to-SMS",
        )

    def test_send_text_raises_key_error_for_invalid_carrier(self) -> None:
        """Test that send_text raises KeyError for unknown carrier."""
        notifier = Notifier(
            smtp_server="smtp.test.com",
            smtp_port=587,
            smtp_username="user",
            smtp_password="pass",
        )

        with pytest.raises(KeyError):
            notifier.send_text(
                sender_email="sender@test.com",
                recipient_phone="5551234567",
                carrier="invalid_carrier",
                subject="Test",
                body="Body",
            )


class TestDefaultNotifier:

    """Tests for DEFAULT_NOTIFIER instance."""

    @patch("praxis.backend.utils.notify.PraxisConfiguration")
    def test_default_notifier_exists(self, mock_config: MagicMock) -> None:
        """Test that DEFAULT_NOTIFIER is created."""
        # This is already imported, but we can verify it's a Notifier
        from praxis.backend.utils.notify import DEFAULT_NOTIFIER

        assert isinstance(DEFAULT_NOTIFIER, Notifier)
