"""Load and firewall NR band profiles.

28 GHz is FR2. SUB6 profiles must be true below-6 GHz. FR1 n96 is not Sub-6.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BANDS_DIR = ROOT / "configs" / "bands"
SIX_GHZ = 6_000_000_000
TWENTY_EIGHT_GHZ = 28_000_000_000


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except Exception:
        from sim.experiments.digital_programme import _mini_yaml_load

        data = _mini_yaml_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Band profile is not a mapping: {path}")
    return data


@dataclass(frozen=True)
class BandProfile:
    data: dict[str, Any]

    @property
    def profile_id(self) -> str:
        return str(self.data["profile_id"])

    @property
    def band_id(self) -> str:
        return str(self.data["band_id"])

    @property
    def family(self) -> str:
        return str(self.data["family"])

    @property
    def fc_hz(self) -> int:
        return int(self.data["fc_hz"])

    @property
    def below_6ghz(self) -> bool:
        return bool(self.data["below_6ghz"])

    @property
    def fr_designation(self) -> str:
        return str(self.data["fr_designation"])

    @property
    def duplex(self) -> str:
        return str(self.data["duplex"])

    @property
    def scs_khz_primary(self) -> int:
        return int(self.data.get("scs_khz_primary") or self.data["scs_khz"][0])

    @property
    def bandwidth_hz_primary(self) -> int:
        return int(self.data["bandwidth_hz_primary"])

    @property
    def experiment_family(self) -> str:
        return str(self.data.get("experiment_family") or self.family)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.data)


def firewall_profile(raw: dict[str, Any], *, path: Path | None = None) -> None:
    loc = str(path) if path else raw.get("profile_id", "<unknown>")
    family = str(raw.get("family"))
    fc = int(raw.get("fc_hz") or 0)
    below = bool(raw.get("below_6ghz"))
    fr = str(raw.get("fr_designation"))
    band_id = str(raw.get("band_id"))
    if fc == TWENTY_EIGHT_GHZ or abs(fc - TWENTY_EIGHT_GHZ) < 1_000_000:
        if family == "SUB6" or below is True:
            raise ValueError(f"{loc}: 28 GHz must never be classified as Sub-6")
        if fr != "FR2" or family != "FR2":
            raise ValueError(f"{loc}: 28 GHz must be FR2")
    if family == "SUB6":
        if not below or fc >= SIX_GHZ:
            raise ValueError(f"{loc}: SUB6 family requires true below-6 GHz fc")
        if fr != "FR1":
            raise ValueError(f"{loc}: SUB6 profiles are FR1 operating bands that are below 6 GHz")
        if band_id == "n96":
            raise ValueError(f"{loc}: n96 is FR1 but not a Sub-6 profile")
    if family == "FR1_NOT_BELOW_6GHZ":
        if below:
            raise ValueError(f"{loc}: FR1_NOT_BELOW_6GHZ cannot set below_6ghz true")
        if raw.get("experiment_family") == "SUB6":
            raise ValueError(f"{loc}: n96-class bands are excluded from SUB6 experiments")
    if family == "FR2" and below:
        raise ValueError(f"{loc}: FR2 cannot be below_6ghz")
    lo, hi = raw.get("range_hz") or [0, 0]
    if not (int(lo) <= fc <= int(hi)):
        raise ValueError(f"{loc}: fc_hz {fc} outside range_hz {[lo, hi]}")


def iter_profile_paths() -> list[Path]:
    return sorted(BANDS_DIR.glob("*/*.yaml"))


def load_profile(path: Path) -> BandProfile:
    raw = _load_yaml(path)
    firewall_profile(raw, path=path)
    return BandProfile(raw)


def load_all_profiles() -> dict[str, BandProfile]:
    out: dict[str, BandProfile] = {}
    for path in iter_profile_paths():
        prof = load_profile(path)
        out[prof.profile_id] = prof
    return out


def profiles_for_family(family: str) -> dict[str, BandProfile]:
    return {k: v for k, v in load_all_profiles().items() if v.family == family}


def primary_sub6() -> BandProfile:
    for prof in load_all_profiles().values():
        if prof.data.get("primary_sub6") is True:
            return prof
    raise KeyError("No primary_sub6 profile")


def fr2_control() -> BandProfile:
    allp = load_all_profiles()
    if "n257_28ghz" in allp:
        return allp["n257_28ghz"]
    raise KeyError("Missing FR2 n257 profile")


def experiment_carrier(profile: BandProfile) -> dict[str, Any]:
    return {
        "frequency_hz": profile.fc_hz,
        "band": profile.fr_designation,
        "family": profile.family,
        "band_id": profile.band_id,
        "profile_id": profile.profile_id,
        "below_6ghz": profile.below_6ghz,
        "label": "Sub-6" if profile.family == "SUB6" else profile.family,
        "never": "Sub-6" if profile.family == "FR2" else "28 GHz as Sub-6",
        "citation": "3GPP TS 38.101-1" if profile.fr_designation == "FR1" else "3GPP TS 38.101-2",
        "scs_khz": profile.scs_khz_primary,
        "bandwidth_hz": profile.bandwidth_hz_primary,
        "duplex": profile.duplex,
    }
