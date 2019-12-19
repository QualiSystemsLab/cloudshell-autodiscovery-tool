import collections
import re

from cloudshell.cli.session.expect_session import ExpectSession

from autodiscovery.exceptions import AutoDiscoveryException


class AbstractDiscoverySession(ExpectSession):
    ENABLE_MODE_COMMAND = "enable"

    def check_credentials(self, cli_credentials, default_prompt, enable_prompt, logger):
        """Connect to the device and check possible credentials.

        :param cli_credentials: list of possible CLI credentials
        :type cli_credentials: autodiscovery.models.VendorCLICredentials
        :param str default_prompt: expected string in output
        :param str enable_prompt: expected string in output for Enable mode
        :param logging.Logger logger:
        :return object with valid user and password for the given device
        :rtype: autodiscovery.models.CLICredentials
        """
        raise NotImplementedError(
            f"Class {type(self)} must implement method 'check_credentials'"
        )

    def _check_enable_password(
        self, enable_prompt, cli_credentials, valid_creds, output_str, logger
    ):
        """Check password for the "enable" mode.

        :param str enable_prompt: prompt for the "enable" mode
        :type cli_credentials: autodiscovery.models.VendorCLICredentials
        :param cli_credentials: list of possible CLI credentials
        :param valid_creds: credentials with a valid user/password
        :type valid_creds: autodiscovery.models.CLICredentials
        :param str output_str: last output from the Device CLI
        :param logging.Logger logger:
        :return object with valid user and password for the given device
        :rtype: autodiscovery.models.CLICredentials
        """
        if enable_prompt:
            action_map = collections.OrderedDict()
            action_map["[Pp]assword:"] = self.prepare_credentials_action_map(
                cli_credentials=cli_credentials,
                valid_creds=valid_creds,
                creds_key="enable_password",
            )

            if not re.search(enable_prompt, output_str, re.DOTALL):
                try:
                    self.hardware_expect(
                        self.ENABLE_MODE_COMMAND,
                        expected_string=enable_prompt,
                        timeout=self._timeout,
                        logger=logger,
                        action_map=action_map,
                        check_action_loop_detector=False,
                    )
                except Exception:
                    logger.warning(
                        "Unable to locate password for the 'enable' mode", exc_info=True
                    )
                    valid_creds.enable_password = None

        return valid_creds

    @staticmethod
    def prepare_credentials_action_map(cli_credentials, valid_creds, creds_key=""):
        """Add valid user/password/enable_password to the valid_creds object.

        :param cli_credentials: list of possible CLI credentials
        :type cli_credentials: autodiscovery.models.VendorCLICredentials
        :param valid_creds: object where valid credentials should be added
        :type valid_creds: autodiscovery.models.CLICredentials
        :param creds_key: key to use in creds object: user/password/enable_password
        :type creds_key: str
        :rtype function
        """
        possible_values = (
            getattr(creds, creds_key)
            for creds in cli_credentials.cli_credentials
            if getattr(creds, creds_key, None)
        )

        def wrapped(session, logger):
            try:
                val = next(possible_values)
            except StopIteration:
                raise AutoDiscoveryException(
                    f"All given credentials aren't valid for the "
                    f"{session.session_type} connection"
                )

            setattr(valid_creds, creds_key, val)
            session.send_line(val, logger)

        return wrapped
