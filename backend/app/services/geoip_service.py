"""
GeoIP lookup service using MaxMind GeoLite2-City database.

If the database file is not present (e.g. during development or first startup),
the service returns a stub response with approximate coordinates based on a
simple country fallback table — so the map still renders test data correctly.
"""

import geoip2.database
import geoip2.errors
import logging
import os

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy-load the GeoIP reader — it's thread-safe after initialization
_reader = None


def _get_reader():
    """Return the GeoIP database reader, initializing if necessary."""
    global _reader
    if _reader is None:
        path = settings.GEOIP_DB_PATH
        if os.path.exists(path):
            try:
                _reader = geoip2.database.Reader(path)
                logger.info(f"[GeoIP] Loaded GeoLite2-City from {path}")
            except Exception as e:
                logger.warning(f"[GeoIP] Failed to load database: {e}")
        else:
            logger.warning(
                f"[GeoIP] Database not found at {path}. "
                "Using stub lookups. Download GeoLite2-City.mmdb from https://www.maxmind.com/en/geolite2/signup"
            )
    return _reader


# ─── Fallback lookup table (country code → approx center coords) ──────────────
_COUNTRY_COORDS = {
    "CN": (35.8617, 104.1954, "China"),
    "RU": (61.5240, 105.3188, "Russia"),
    "US": (37.0902, -95.7129, "United States"),
    "IN": (20.5937, 78.9629, "India"),
    "DE": (51.1657, 10.4515, "Germany"),
    "BR": (-14.2350, -51.9253, "Brazil"),
    "GB": (55.3781, -3.4360, "United Kingdom"),
    "FR": (46.2276, 2.2137, "France"),
    "KR": (35.9078, 127.7669, "South Korea"),
    "JP": (36.2048, 138.2529, "Japan"),
    "NG": (9.0820, 8.6753, "Nigeria"),
    "UA": (48.3794, 31.1656, "Ukraine"),
    "NL": (52.1326, 5.2913, "Netherlands"),
    "PK": (30.3753, 69.3451, "Pakistan"),
    "VN": (14.0583, 108.2772, "Vietnam"),
    "BD": (23.6850, 90.3563, "Bangladesh"),
    "TR": (38.9637, 35.2433, "Turkey"),
    "IR": (32.4279, 53.6880, "Iran"),
    "ID": (-0.7893, 113.9213, "Indonesia"),
    "MX": (23.6345, -102.5528, "Mexico"),
}


def lookup_ip(ip: str) -> dict:
    """
    Look up geographic information for an IP address.

    Returns:
        dict with keys: country, country_code, city, latitude, longitude
    """
    reader = _get_reader()

    # Skip private / reserved IPs
    if _is_private(ip):
        return _stub("Local Network", "LO", "Localhost", 0.0, 0.0)

    if reader:
        try:
            response = reader.city(ip)
            return {
                "country":      response.country.name or "Unknown",
                "country_code": response.country.iso_code or "XX",
                "city":         response.city.name or "Unknown",
                "latitude":     float(response.location.latitude or 0),
                "longitude":    float(response.location.longitude or 0),
            }
        except geoip2.errors.AddressNotFoundError:
            pass
        except Exception as e:
            logger.debug(f"[GeoIP] Lookup failed for {ip}: {e}")

    # Stub fallback — try to guess from IP range for test data
    return _fallback_lookup(ip)


def _is_private(ip: str) -> bool:
    """Check if the IP is in a private/reserved range."""
    try:
        parts = list(map(int, ip.split(".")))
        if parts[0] == 10:
            return True
        if parts[0] == 172 and 16 <= parts[1] <= 31:
            return True
        if parts[0] == 192 and parts[1] == 168:
            return True
        if parts[0] == 127:
            return True
    except Exception:
        pass
    return False


def _fallback_lookup(ip: str) -> dict:
    """Return a best-effort stub based on IP octet patterns."""
    # Cycle through country list for test data variety
    try:
        first_octet = int(ip.split(".")[0])
        countries = list(_COUNTRY_COORDS.items())
        idx = first_octet % len(countries)
        code, (lat, lon, name) = countries[idx]
        return _stub(name, code, "Unknown", lat, lon)
    except Exception:
        return _stub("Unknown", "XX", "Unknown", 0.0, 0.0)


def _stub(country, code, city, lat, lon):
    return {
        "country":      country,
        "country_code": code,
        "city":         city,
        "latitude":     lat,
        "longitude":    lon,
    }
