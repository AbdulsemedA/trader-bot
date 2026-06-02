"""Binance Futures Testnet API client with HMAC-SHA256 request signing."""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
ACCOUNT_ENDPOINT = "/fapi/v2/account"

REQUEST_TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, code: int, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message} (HTTP {status_code})")


class BinanceFuturesClient:
    """Wrapper around the Binance Futures Testnet REST API.

    Handles request signing (HMAC-SHA256), timestamping, and error handling.

    Args:
        api_key: Binance Futures Testnet API key.
        api_secret: Binance Futures Testnet API secret.
    """

    def __init__(self, api_key: str, api_secret: str) -> None:
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = BASE_URL

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _sign(self, params: dict) -> dict:
        """Add timestamp and HMAC-SHA256 signature to request parameters.

        Args:
            params: Request parameters to sign.

        Returns:
            Parameters with timestamp and signature appended.
        """
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: dict | None = None) -> dict:
        """Execute a signed API request.

        Args:
            method: HTTP method (GET, POST, DELETE).
            endpoint: API endpoint path.
            params: Request parameters.

        Returns:
            Parsed JSON response.

        Raises:
            BinanceAPIError: If the API returns an error.
            requests.RequestException: On network-level failures.
        """
        params = params or {}
        signed_params = self._sign(params)
        url = f"{self.base_url}{endpoint}"

        logger.debug("REQUEST  %s %s | params=%s", method, url, signed_params)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=signed_params if method == "GET" else None,
                data=signed_params if method != "GET" else None,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.ConnectionError as exc:
            logger.error("Network error connecting to %s: %s", url, exc)
            raise
        except requests.Timeout as exc:
            logger.error("Request timed out for %s: %s", url, exc)
            raise

        logger.debug("RESPONSE %s | status=%s | body=%s", url, response.status_code, response.text)

        data = response.json()

        if response.status_code >= 400:
            error_code = data.get("code", -1)
            error_msg = data.get("msg", "Unknown error")
            logger.error(
                "API error: code=%s msg='%s' http_status=%s",
                error_code,
                error_msg,
                response.status_code,
            )
            raise BinanceAPIError(response.status_code, error_code, error_msg)

        return data

    def place_order(self, **params: str | float) -> dict:
        """Place an order on Binance Futures Testnet.

        Args:
            **params: Order parameters (symbol, side, type, quantity, price, etc.).

        Returns:
            Order response from the API.
        """
        logger.info("Placing order: %s", params)
        result = self._request("POST", ORDER_ENDPOINT, dict(params))
        logger.info("Order placed successfully: orderId=%s", result.get("orderId"))
        return result

    def get_account_info(self) -> dict:
        """Retrieve account information.

        Returns:
            Account details from the API.
        """
        return self._request("GET", ACCOUNT_ENDPOINT)
