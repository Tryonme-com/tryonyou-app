import unittest
from unittest.mock import patch, MagicMock
import io
import base64

from disparar_desde_personal import enviar_soberania

class TestDispararDesdePersonal(unittest.TestCase):
    @patch('disparar_desde_personal.require_smtp_credentials')
    @patch('disparar_desde_personal.smtplib.SMTP')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_enviar_soberania_success(self, mock_stdout, mock_smtp, mock_require_credentials):
        # Arrange
        mock_require_credentials.return_value = ('test@example.com', 'test_password')
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Act
        enviar_soberania()

        # Assert
        mock_require_credentials.assert_called_once()
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'test_password')

        # Check that sendmail was called correctly
        self.assertEqual(mock_server.sendmail.call_count, 1)
        args, kwargs = mock_server.sendmail.call_args
        self.assertEqual(args[0], 'test@example.com')
        self.assertListEqual(
            args[1],
            ["nicolas.houze@lafayette.fr", "g.houze@lafayette.fr", "egandini@lafayette.fr", "test@example.com"]
        )
        # Content is base64 encoded by MIMEText
        self.assertIn("33.200".encode('utf-8'), base64.b64decode(args[2].split("Content-Transfer-Encoding: base64")[1].split("--==")[0].strip()))

        mock_server.quit.assert_called_once()
        self.assertIn("✅ PROTOCOLO ENVIADO DESDE GMAIL PERSONAL. ÉXITO.", mock_stdout.getvalue())

    @patch('disparar_desde_personal.require_smtp_credentials')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_enviar_soberania_failure(self, mock_stdout, mock_require_credentials):
        # Arrange
        mock_require_credentials.side_effect = Exception("Credenciales no encontradas")

        # Act
        enviar_soberania()

        # Assert
        self.assertIn("❌ ERROR: Credenciales no encontradas", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
