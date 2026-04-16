from __future__ import annotations

import math


class SVY21:
    """Convert Singapore SVY21 northing/easting to WGS84 latitude/longitude."""

    A = 6378137.0
    F = 1 / 298.257223563
    ORIGIN_LAT = 1.366666
    ORIGIN_LON = 103.833333
    FALSE_NORTHING = 38744.572
    FALSE_EASTING = 28001.642
    SCALE = 1.0

    def __init__(self) -> None:
        self.b = self.A * (1 - self.F)
        self.e2 = (2 * self.F) - (self.F * self.F)
        self.e4 = self.e2 * self.e2
        self.e6 = self.e4 * self.e2
        self.a0 = 1 - (self.e2 / 4) - (3 * self.e4 / 64) - (5 * self.e6 / 256)
        self.a2 = (3.0 / 8.0) * (self.e2 + (self.e4 / 4.0) + (15 * self.e6 / 128.0))
        self.a4 = (15.0 / 256.0) * (self.e4 + (3 * self.e6 / 4.0))
        self.a6 = 35 * self.e6 / 3072.0

    def _meridional_arc(self, latitude_deg: float) -> float:
        latitude_rad = math.radians(latitude_deg)
        return self.A * (
            (self.a0 * latitude_rad)
            - (self.a2 * math.sin(2 * latitude_rad))
            + (self.a4 * math.sin(4 * latitude_rad))
            - (self.a6 * math.sin(6 * latitude_rad))
        )

    def _rho(self, sin2_lat: float) -> float:
        return self.A * (1 - self.e2) / ((1 - self.e2 * sin2_lat) ** 1.5)

    def _v(self, sin2_lat: float) -> float:
        return self.A / math.sqrt(1 - self.e2 * sin2_lat)

    def to_latlon(self, northing: float, easting: float) -> tuple[float, float]:
        northing_prime = northing - self.FALSE_NORTHING
        meridional_prime = self._meridional_arc(self.ORIGIN_LAT) + (northing_prime / self.SCALE)

        n = (self.A - self.b) / (self.A + self.b)
        n2 = n * n
        n3 = n2 * n
        n4 = n2 * n2

        g = self.A * (1 - n) * (1 - n2) * (1 + (9 * n2 / 4) + (225 * n4 / 64)) * (math.pi / 180)
        sigma = (meridional_prime * math.pi) / (180 * g)

        latitude_prime = (
            sigma
            + ((3 * n / 2) - (27 * n3 / 32)) * math.sin(2 * sigma)
            + ((21 * n2 / 16) - (55 * n4 / 32)) * math.sin(4 * sigma)
            + (151 * n3 / 96) * math.sin(6 * sigma)
            + (1097 * n4 / 512) * math.sin(8 * sigma)
        )

        sin_lat_prime = math.sin(latitude_prime)
        sin2_lat_prime = sin_lat_prime * sin_lat_prime
        rho_prime = self._rho(sin2_lat_prime)
        v_prime = self._v(sin2_lat_prime)
        psi_prime = v_prime / rho_prime
        psi2 = psi_prime * psi_prime
        psi3 = psi2 * psi_prime
        psi4 = psi3 * psi_prime
        tan_lat_prime = math.tan(latitude_prime)
        tan2 = tan_lat_prime * tan_lat_prime
        tan4 = tan2 * tan2
        tan6 = tan4 * tan2

        easting_prime = easting - self.FALSE_EASTING
        x = easting_prime / (self.SCALE * v_prime)
        x2 = x * x
        x3 = x2 * x
        x5 = x3 * x2
        x7 = x5 * x2

        latitude_factor = tan_lat_prime / (self.SCALE * rho_prime)
        latitude = (
            latitude_prime
            - latitude_factor * ((easting_prime * x) / 2)
            + latitude_factor * ((easting_prime * x3) / 24) * ((-4 * psi2) + (9 * psi_prime) * (1 - tan2) + (12 * tan2))
            - latitude_factor
            * ((easting_prime * x5) / 720)
            * (
                (8 * psi4) * (11 - 24 * tan2)
                - (12 * psi3) * (21 - 71 * tan2)
                + (15 * psi2) * (15 - 98 * tan2 + 15 * tan4)
                + (180 * psi_prime) * (5 * tan2 - 3 * tan4)
                + 360 * tan4
            )
            + latitude_factor * ((easting_prime * x7) / 40320) * (1385 - 3633 * tan2 + 4095 * tan4 + 1575 * tan6)
        )

        sec_latitude = 1 / math.cos(latitude)
        longitude = (
            math.radians(self.ORIGIN_LON)
            + x * sec_latitude
            - ((x3 * sec_latitude) / 6) * (psi_prime + 2 * tan2)
            + ((x5 * sec_latitude) / 120)
            * ((-4 * psi3) * (1 - 6 * tan2) + psi2 * (9 - 68 * tan2) + 72 * psi_prime * tan2 + 24 * tan4)
            - ((x7 * sec_latitude) / 5040) * (61 + 662 * tan2 + 1320 * tan4 + 720 * tan6)
        )

        return math.degrees(latitude), math.degrees(longitude)
