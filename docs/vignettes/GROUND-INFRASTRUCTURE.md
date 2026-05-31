# Ground Infrastructure — Realistic Placement Reference

[← Vignettes index](INDEX.md) · [↑ Docs index](../INDEX.md)

This document catalogs the **realistic, open-source-derived coordinates** used for ground
stations, sensors, jammers, and DA-ASAT sites across the vignette library. Every entry here is
publicly known basing data — no classified material, no operational details.

> **Sources:** Wikipedia, GlobalSecurity.org, Secure World Foundation *Global Counterspace
> Capabilities* (2025/26), CSIS *Space Threat Assessment*, AMTI (Asia Maritime Transparency
> Initiative), commercial satellite imagery analyses (Planet, BlackSky, ESRI). Coordinates are
> typically rounded to 2 decimal places (≈1 km precision) — exact enough for orbital geometry,
> generic enough to remain unclassified.

---

## 1. Blue / coalition TT&C and downlink sites

| Code | Real-world site | Lat | Lon | Used by vignettes |
|---|---|---|---|---|
| Vandenberg | Vandenberg SFB (AFSCN RTS), CA | 34.74 | -120.57 | `mt-sigint-geolocate` (GS-MIDLAT) |
| Schriever | Schriever SFB (AFSCN master), CO | 38.81 | -104.53 | `coa-russia-md` (GS-PRIME) |
| New Boston | New Boston AFS (AFSCN), NH | 42.95 | -71.63 | (available) |
| Kaena Point | Kaena Point AFSCN (HTS), Oahu HI | 21.57 | -158.24 | `learn-intermediate-recovery` (GS-LEARN) |
| Guam GTS | Andersen AFB AFSCN, Guam | 13.62 | 144.86 | `01-leo-isr-denial`, `08-multi-domain-taiwan` (GS-EAST), `coa-china-ml`, `coa-china-md` (GS-WESTPAC / GS-WP) |
| Diego Garcia | AFSCN REEF + GEODSS Det 2, BIOT | -7.41 | 72.45 | `01-leo-isr-denial` (GS-EAST in updated layout) |
| Pituffik (Thule) | AFSCN POGO + UEWR, Greenland | 76.53 | -68.70 | (available) |
| Oakhanger | RAF Oakhanger (UK Skynet/NATO) | 51.12 | -0.89 | `coa-russia-ml` (GS-EUROPE) |
| Kourou | CSG Kourou (CNES/ESA), French Guiana | 5.24 | -52.77 | `00-training-basics` (GS-TRN), `nv-isl-relay-debris`, `learn-intermediate-recovery` (GS-LEARN) |
| Al Dhafra | Al Dhafra AFB (USAF), UAE | 24.25 | 54.55 | `01-leo-isr-denial`, `08-multi-domain-taiwan` (GS-NORTH) |
| SvalSat | Svalbard Satellite Station (KSAT), Norway | 78.23 | 15.39 | `mt-isr-sar` (GS-POLAR) |
| Inuvik | Inuvik Satellite Station, NWT Canada | 68.32 | -133.55 | (available) |
| McMurdo | NASA NEN McMurdo, Antarctica | -77.85 | 166.67 | (available) |
| TrollSat | KSAT Troll, Antarctica | -72.01 | 2.53 | (available) |
| Fairbanks AK | Fairbanks polar downlink (NEN), AK | 64.86 | -147.85 | `mt-weather-collect` (GS-WX-BACKUP) |
| Wallops/Suitland | Wallops Flight Facility / NOAA NSOF, VA-MD | 37.94 | -75.46 | `mt-weather-collect` (GS-WX-PRIMARY) |
| Al Yah (Al Ain) | Yahsat / coalition teleport, UAE | 24.21 | 55.74 | `coa-misc-iran-ml` (GS-GULF) |

## 2. US Space Surveillance Network (SSN) sensor sites

| Code | Real-world site | Lat | Lon | Used by vignettes |
|---|---|---|---|---|
| GEODSS-Socorro | GEODSS Det 1 (optical), NM | 33.82 | -106.66 | `07-sda-custody-hunt` (BLUE-OPT-1) |
| GEODSS-Maui | AMOS / Haleakalā, HI | 20.71 | -156.26 | `02-geo-rpo-shadowing`, `08-multi-domain-taiwan`, `coa-china-ml`, `coa-china-md` (BLUE-OPT / BLUE-OPTICAL / BLUE-OPTICAL-WP) |
| GEODSS-Diego | GEODSS Det 2, BIOT | -7.41 | 72.45 | (available) |
| CapeCodSFS | Cape Cod SFS (PAVE PAWS UEWR), MA | 41.75 | -70.54 | `coa-russia-md` (BLUE-RADAR-W), `06-satcom-cyber-link` (BLUE-RADAR) |
| Beale | Beale AFB (PAVE PAWS UEWR), CA | 39.14 | -121.35 | (available) |
| Clear | Clear SFS (LRDR), AK | 64.30 | -149.19 | (available) |
| Fylingdales | RAF Fylingdales (UEWR), UK | 54.36 | -0.67 | `04-co-orbital-threat-escort`, `coa-russia-ml`, `coa-russia-md` (BLUE-RADAR / -EU / -E) |
| Cavalier | Cavalier SFS (PARCS), ND | 48.72 | -97.90 | `03-gnss-ew-campaign` (BLUE-RADAR) |
| Eglin | Eglin AFB AN/FPS-85, FL | 30.57 | -86.21 | `07-sda-custody-hunt` (BLUE-RADAR-1) |
| Globus II | Vardø Globus II (X-band SSA), Norway | 70.37 | 31.13 | (available) |

## 3. Russian counterspace / SDA / EW sites

| Code | Real-world site | Lat | Lon | Used by vignettes |
|---|---|---|---|---|
| Plesetsk | Plesetsk (Nudol DA-ASAT) | 62.93 | 40.57 | `coa-russia-md` (RED-NUDOL), `05-da-asat-crisis` (RED-ASAT) |
| Don-2N | Don-2N Pushkino (ABM/SSA radar) | 56.17 | 37.77 | (available) |
| Krona | Krona Zelenchukskaya (optical+radar SSA) | 43.65 | 41.43 | (available) |
| Okno | Okno Nurek (optical SSA), Tajikistan | 38.27 | 69.27 | (available) |
| Kaliningrad | Baltiysk / Kaliningrad (Tirada/Pole-21 reference) | 54.71 | 20.51 | `coa-russia-ml` (RED-JAM-TIRADA), `coa-russia-md` (RED-JAM), `03-gnss-ew-campaign` (RED-JAM) |
| Dzhankoy | Dzhankoy area (reported Pole-21), Crimea | 45.71 | 34.39 | `coa-russia-ml` (RED-JAM-BYLINA) |
| Khmeimim | Khmeimim Air Base (Krasukha/Tirada), Syria | 35.40 | 35.95 | (available) |
| Voronezh-Armavir | Voronezh-DM (early-warning array), S. Russia | 44.92 | 40.99 | (available) |
| Voronezh-Lekhtusi | Voronezh-M (early-warning array), NW Russia | 60.28 | 30.55 | (available) |

## 4. Chinese (PLA) counterspace / launch / EW sites

| Code | Real-world site | Lat | Lon | Used by vignettes |
|---|---|---|---|---|
| Korla | Korla SSA radar (SC-19 test region), Xinjiang | 41.64 | 86.24 | `01-leo-isr-denial` (RED-ASAT) |
| Kashgar | Kashgar (Shule) tracking, Xinjiang | 39.51 | 76.03 | (available) |
| Jiuquan | Jiuquan SLC (SC-19/DN DA-ASAT tests) | 40.96 | 100.29 | `08-multi-domain-taiwan` (RED-ASAT), `coa-china-md` (RED-ASAT) |
| Xichang | Xichang SLC | 28.25 | 102.03 | (available) |
| Taiyuan | Taiyuan SLC | 38.85 | 111.61 | (available) |
| Wenchang | Wenchang SLS, Hainan | 19.61 | 110.95 | (available) |
| Woody Island | Yongxing / Paracels (reported EW) | 16.83 | 112.34 | `coa-china-ml` (RED-JAM-COASTAL), `coa-china-md` (RED-JAM-PNT) |
| Fiery Cross | Fiery Cross Reef (reported jammers), Spratlys | 9.55 | 112.89 | `01-leo-isr-denial` (JAM-NORTH), `08-multi-domain-taiwan` (JAM-NORTH) |
| Yulin Hainan | Yulin Naval Base (PLAN HQ), Hainan | 18.23 | 109.70 | `mt-sigint-geolocate` (RED-EMITTER) |
| Jiamusi | Jiamusi 66 m deep-space dish, Heilongjiang | 46.49 | 130.77 | (available) |

## 5. Misc actor sites (Iran / DPRK / India / France / etc.)

| Code | Real-world site | Lat | Lon | Used by vignettes |
|---|---|---|---|---|
| Bandar Abbas | Iranian Navy HQ (EW vessels), Strait of Hormuz | 27.13 | 56.21 | `coa-misc-iran-ml` (RED-MOBILE-JAM-1), `01-leo-isr-denial`, `08-multi-domain-taiwan` (JAM-NORTH) |
| Isfahan | Iranian inland EW (IRGC), Esfahan | 32.65 | 51.67 | `coa-misc-iran-ml` (RED-MOBILE-JAM-2) |
| Semnan | Imam Khomeini Spaceport, Iran | 35.24 | 53.95 | (available) |
| Sohae | DPRK Tongchang-ri launch site | 39.66 | 124.71 | (available) |
| Sriharikota | ISRO SDSC SHAR, India | 13.73 | 80.23 | (available) |
| Wheeler Island | Mission Shakti DA-ASAT test site, Odisha | 20.76 | 87.09 | (available) |

## 6. Auto-generated SSN sites (from `engine/ssn.py`)

The `instantiate_network()` function in `spacesim/engine/ssn.py` procedurally generates per-cell
SSN sensors based on the `ssn_blue_dispersion` / `ssn_red_dispersion` vignette parameters. These
coordinates are already realistic — they correspond to:

**Radars (`_radar_sites()`):**
- `(34.0, -120.6)` ≈ Vandenberg SFB
- `(30.5, -86.5)` ≈ Eglin AFB
- `(51.5, -1.0)` ≈ RAF Fylingdales (UK)
- `(35.7, 139.7)` ≈ Yokota AB area, Japan (added at *regional* dispersion)
- `(-31.9, 115.9)` ≈ Perth, Australia (added at *global*)
- `(-33.9, 18.4)` ≈ Cape Town, South Africa (added at *proliferated*)
- `(28.6, 77.2)` ≈ New Delhi area, India (added at *proliferated*)
- `(64.1, -21.9)` ≈ Reykjavík, Iceland (added at *proliferated*)

**Optical (`_optical_sites()`):**
- `(20.7, -156.3)` ≈ GEODSS Maui / AMOS, Haleakalā
- `(32.7, -16.9)` ≈ Madeira / Tenerife region
- `(-23.3, 16.5)` ≈ Gobabeb / Hakos, Namibia (added at *global*)
- `(-43.5, 172.6)` ≈ Mount John / Tekapo, NZ (added at *global*)
- `(40.5, 23.0)` ≈ Mt Holomon area, Greece (added at *proliferated*)
- `(37.2, -3.0)` ≈ Sierra Nevada, Spain (added at *proliferated*)

No changes required for the SSN code layer; the dispersion presets already track real
observatories and military radar sites.

---

## 7. Authoring rules for new vignettes

When designing a new vignette, pick ground coordinates **from this catalog** wherever possible
rather than inventing fictional lat/lon. Rationale:

1. **Realism.** Trainees recognise the names ("Cape Cod radar," "Plesetsk") and the geography
   feels right.
2. **Cross-vignette consistency.** When a player sees `BLUE-RADAR-CC` in two different vignettes
   they should be at the same real radar site.
3. **Doctrinal correctness.** Russian EW belongs in Russia; PLA RPO inspectors launch from
   Chinese sites; Iranian jammers don't live in Crimea. The catalog enforces this.
4. **Open-source only.** Every entry above is from public reporting. Future contributors should
   not add classified coordinates; if a site isn't in this catalog, it isn't appropriate for
   this simulator.

If you need a site outside the catalog, add it to the table above first (with source), then
reference it from your vignette YAML.

---

## 8. Co-located jammer convention

Several vignettes intentionally co-locate a Red jammer with a Blue ground station to ensure the
jammer's footprint covers the downlink window. When using realistic coordinates, place the
jammer **within ~50 km** of the Blue station (same theater, same horizon mask) so the geometry
still works. Don't perfectly co-locate (offsets create realistic-feeling threat geography).

Where the Blue and Red elements should be at **truly distinct** real sites (e.g. Guam-based GS
vs. Spratly-based jammer), the distance is large but the orbital pass still covers both — the
geometry validates this naturally.
