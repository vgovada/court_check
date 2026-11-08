# CourtCheck

**How dusty are the Texas A&M Rec Center courts, and when is the safest time to play?**

CourtCheck is an interactive website built on data we collected ourselves at the Texas A&M Rec Center during TAMU Datathon. We wiped the courts with white cloths, measured how dirty each cloth got from photos, and measured shoe grip with a spring scale. The website turns those measurements into simple answers:

- **Casual or injured players:** which court and time of day has the least slippery floor.
- **Basketball players:** which of the basketball courts is cleaner at a given time.
- **Rec staff:** which courts need cleaning first.

---

## Quick start

Requires Python 3.9 or newer.

```bash
git clone https://github.com/vgovada/court_check.git
cd court_check

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app/app.py
```

The site opens in your browser at `http://localhost:8501`. Press **Ctrl + C** in the terminal to stop it.

To recompute the discoloration index from the cloth photos:

```bash
python src/discoloration.py
```

This reads `data/photos/` and `data/blanks/` and writes `data/discoloration.csv`.

---

## What the website does

The whole site is one scrolling page:

1. **Intro and scroll animation:** a sneaker on a hardwood floor. As you scroll, dust settles, a grip meter drops, and the shoe slides, showing why dust matters.
2. **Find your court:** pick a time (4 PM, 7 PM, 10 PM) and who you are. The site recommends a court, shows every court's dust level and slip risk, and opens a detail panel for any court you tap.
3. **By the numbers:** headline statistics, a scatter plot of friction against discoloration, and a bar chart comparing courts.
4. **How we did it:** our method, the cloth photos, a "grocery list" of the tools we used, and the raw data table.
5. **Credits:** the team.

Every number on the site is read from `data/court_data.csv` and `data/photos/` when the app starts. Nothing is typed into the page by hand.

---

## Data collection methodology

**Where:** Texas A&M Rec Center indoor courts. We tested 6 court types across 16 courts: Basketball A (courts 1–4), Volleyball (5a–6b), Pickleball (7a–7c), Badminton (8a–8c), Soccer/futsal (9) and Basketball B (10).

**When:** In the afternoon, around 4 PM. Rec staff clean the courts around noon and again around 7 PM; badminton courts are not cleaned in the evening.

**Dust (discoloration index)**

1. On each court we wiped 2 or 3 same-size patches of floor with a clean white washcloth, using the same strokes and pressure every time. **42 cloth samples in total.**
2. We photographed the cloths, along with one clean, unused cloth (`data/blanks/`) as the reference.
3. `src/discoloration.py` uses OpenCV to crop the center of each photo, correct for lighting (so the brightest 1% of pixels becomes white), and convert it to the CIELAB color space.
4. **Discoloration index = lightness (L\*) of the clean cloth − lightness of the used cloth.** 0 means spotless; higher means dustier.

**Grip (friction)**

1. We put a full water bottle inside a basketball shoe so the shoe weighed **3.0 lb** in total.
2. We pulled the shoe sideways across the floor with a spring scale and recorded the force at the moment it started to slide.
3. On a clean floor it took **3.25 lb**.
4. **Coefficient of friction = pull force ÷ shoe weight (3.0 lb).** Higher means more grip.

**Values shown on the site**

- **Dust %** = how much grip a court lost compared with the clean floor: `(3.25 − pull force) ÷ 3.25 × 100`.
- **Slip risk** labels: Low (under 10%), Moderate (10–30%), High (30–50%), Severe (50% and above).
- Each court group's values are the average of the samples taken on that group of courts.

---

## Measured vs. projected data

> **Only the 4 PM values were measured. The 7 PM and 10 PM values are projected (synthetic).** They are labeled "projected" in the data file headers and on the website.

The 7 PM and 10 PM values were generated from the 4 PM measurements and the Rec's cleaning schedule:

- Dust builds up with time since the last cleaning, at each court's measured 4 PM rate (4 hours since the noon clean).
- At 7 PM, every court except badminton is cleaned. Cleaning removes most of the dust, less thoroughly on pickleball courts.
- From 7 PM to 10 PM, dust builds up again, faster on busier courts (heavy evening play on Basketball A and badminton, light play on soccer).
- Projected friction is scaled between the clean-floor value (3.25 lb) and each court's measured 4 PM friction.

---

## Data dictionary

### `data/court_data.csv`

Spreadsheet layout: each court group's values are on the first row of the group, and the rows below it list the other courts in that group. The last row holds the two reference measurements.

| Column | Type | Description |
|---|---|---|
| `Court #` | text | Court number at the Rec (e.g. `1`, `5a`) |
| `Court Type` | text | Sport, filled in on the first row of each group. The second `Basketball` group is shown on the site as Basketball B |
| `Samples` | integer | Number of cloth samples taken on that court (2 or 3). The total row sums to 42 |
| `4 PM discoloration` | number | Discoloration index at 4 PM (measured) |
| `4 PM friction (lb)` | number | Spring-scale force to make the 3.0 lb shoe slide at 4 PM (measured) |
| `4 PM coef` | number | Coefficient of friction at 4 PM = friction ÷ 3.0 |
| `7 PM discoloration (projected)` | number | Projected discoloration index at 7 PM |
| `7 PM friction (lb) (projected)` | number | Projected pull force at 7 PM |
| `7 PM coef (projected)` | number | Projected coefficient of friction at 7 PM |
| `10 PM discoloration (projected)` | number | Projected discoloration index at 10 PM |
| `10 PM friction (lb) (projected)` | number | Projected pull force at 10 PM |
| `10 PM coef (projected)` | number | Projected coefficient of friction at 10 PM |
| `Friction Clean` row | number | Pull force on a clean floor: 3.25 lb |
| `Shoe+bottle` row | number | Weight of the shoe plus water bottle: 3.0 lb |

### `data/discoloration.csv` (output of `src/discoloration.py`)

| Column | Type | Description |
|---|---|---|
| `photo_file` | text | Cloth photo filename in `data/photos/` |
| `mean_lightness` | number | Average CIELAB lightness (L\*, 0–100) of the cloth after lighting correction |
| `discoloration_index` | number | Clean-cloth lightness minus this cloth's lightness. Higher = dustier |
| `dust_pixel_pct` | number | Percent of pixels at least 10 L\* units darker than the clean cloth |

### Photos

- `data/photos/`: one cloth photo per court group, named by court (e.g. `pickleball_cloth.jpg`).
- `data/blanks/`: the clean reference cloth.
- `app/images/`: team headshots and project photos for the Credits section. Everyone shown is a team member.

---

## Key findings

- Dustier cloths lined up closely with slipperier floors: across the 6 measured court groups, discoloration and friction have a correlation of **r = −0.98**.
- **Pickleball** left the dirtiest cloth (discoloration 7.2), about 2.7× dirtier than **soccer** (2.7), the cleanest. Pickleball courts are shared with futsal, players wear everyday sneakers that track in outside dirt, and cleaning crews prioritize basketball and volleyball.
- At 4 PM the dustiest court lost **60%** of its grip compared with a clean floor.

---

## Limitations

- **Small sample:** 2–3 cloth samples per court, averaged per court group. Good for comparing courts, not for precise values.
- **Projected times:** 7 PM and 10 PM are modeled from one afternoon of measurements and the cleaning schedule, not measured.
- **One day:** usage and cleaning vary by day and season; we measured on a single weekend afternoon.
- **Phone photos:** taken under gym lighting. The code corrects for overall brightness, but shadows and color casts can still affect the index.
- **Homemade friction test:** a spring scale and a water-bottle-weighted shoe, read by eye at the moment of slipping. It approximates grip; it is not lab equipment.
- **One shoe:** results may differ with other soles, and basketball shoes grip better than the everyday sneakers many casual players wear.

---

## Project structure

```
court_check/
├── app/
│   ├── app.py            # Streamlit entry point: loads data and photos, serves the page
│   ├── data.py           # Reads court_data.csv and computes dust %, levels, best times
│   ├── site.html         # The interactive one-page website (HTML, CSS, JavaScript)
│   ├── fonts/            # Caveat handwriting font (SIL Open Font License)
│   └── images/           # Team headshots and project photos
├── data/
│   ├── court_data.csv    # Main dataset (4 PM measured, 7/10 PM projected)
│   ├── discoloration.csv # Output of src/discoloration.py
│   ├── photos/           # Used cloth photos
│   └── blanks/           # Clean reference cloth
├── src/
│   └── discoloration.py  # Turns cloth photos into a discoloration index (OpenCV)
├── .streamlit/config.toml
├── requirements.txt
└── README.md
```

---

## Built with

Python, Streamlit, OpenCV, NumPy and pandas, with the front end in plain HTML, CSS and JavaScript (no external charting libraries). Handwriting font: [Caveat](https://github.com/googlefonts/caveat), SIL Open Font License 1.1.

---

## Team

- **Vidhur Govada**, Computer Science '28
- **Joseph Gwak**, Mechanical Engineering '28
- **William Lee**, Applied Math / Actuarial Science '28

Built at TAMU Datathon.