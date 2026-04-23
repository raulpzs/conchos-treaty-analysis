# Rio Conchos Water Crisis: A 110-Year Decomposition

**Author:** Raul Alejandro Pérez Saucedo
**Contact:** raulpzs@outlook.com

---

## What this project is

The 1944 Water Treaty between Mexico and the United States requires Mexico to deliver an average of 350,000 acre-feet of water per year from the Rio Conchos and other tributaries into the Rio Grande. In 2025, Mexico ended its most recent five-year delivery cycle having sent only 50% of what it owed. It's the worst shortfall in recent treaty history, triggering U.S. tariff threats and an emergency bilateral agreement. Mexico has cited drought and climate stress; U.S. officials have recognized climate change but also emphasized compliance and predictability.

This project tests that explanation against 110 years of data.

Using reconstructed naturalized and regulated streamflow records for the Rio Conchos at Ojinaga (1901–2010), it decomposes Mexico's recurring delivery failures into its causes: natural water availability versus upstream agricultural extraction. The findings suggest that the treaty's current failure cannot be explained solely through climate change, historical extraction and allocation patterns made the system structurally fragile long before the present climate crisis arrived.

---

## Core findings

Natural flow at the Ojinaga gauge, which is the water the Rio Conchos basin produces before human extraction, exceeded the treaty's annual target in **every single year** of the 110-year record. Regulated flow, the water that actually reaches the border, fell below the same target in **20 years**, all concentrated in the post-1950 period as irrigated agriculture expanded. The share of natural flow captured before reaching the border grew from **24% in the pre-treaty period** to **72% after 1990**.

The basin has always had enough water. The crisis is a delivery failure, not a supply failure.

---

## Data sources

| Dataset | Source | Period |
|---------|--------|--------|
| Naturalized & regulated monthly streamflow, Rio Conchos at Ojinaga | [CUAHSI HydroShare](https://www.hydroshare.org/resource/89728c8779c644d7a6ce110406516849/) — Garza Díaz (2022) | 1900–2010 |
| Naturalized & regulated monthly streamflow, Above Amistad | Same HydroShare resource | 1900–2010 |
| Treaty cycle delivery data (2020–2025) | [IBWC Water Data](https://www.ibwc.gov/water-data/) | 2020–2025 |
| Amistad-Falcon reservoir ownership | IBWC Water Data | 1996–present |

**Important limitation:** The naturalized flow dataset ends in 2010. The 2011–2025 period cannot be decomposed using this methodology. See the methods appendix in `brief/` for full discussion.

---

## How to reproduce

### Requirements
```
python >= 3.10
pandas
numpy
matplotlib
```

Install with:
```bash
pip install pandas numpy matplotlib
```

### Run order
```
notebooks/01_data_processing.ipynb    # loads raw CSVs, converts units, builds master dataset
notebooks/02_exploratory_analysis.ipynb   # summary statistics and data quality checks  
notebooks/03_findings_figures.ipynb   # produces all figures in figures/
```

All figures in `figures/` are fully reproducible from the raw data files in `data/raw/`.

---

## Repository structure

```
├── data/
│   ├── raw/          original HydroShare CSVs, unmodified
│   └── processed/    cleaned annual datasets produced by notebook 01
├── notebooks/        analysis in order
├── figures/          all output figures
├── brief/            policy brief draft and methods appendix
└── src/              reusable processing functions
```

---

## Citation

If you use this data or analysis, please cite:

> Pérez Saucedo, R.A. (2026). *A decomposition of natural availability and extraction of the Rio Conchos under the 1944 US-Mexico Water Treaty*. Working paper. Available at: github.com/raulpzs/conchos-treaty-analysis

And the underlying dataset:

> Garza Díaz, L.E. (2021/2022). *Natural and Regulated Streamflow Data for the Rio Grande / Rio Bravo Basin*. CUAHSI HydroShare. https://www.hydroshare.org/resource/89728c8779c644d7a6ce110406516849/

---

## License

MIT License. Data from HydroShare is subject to its original terms of use.
