---
title: 'raddo: A Python package for RADOLAN weather radar data provision'
tags:
  - Python
  - weather radar
  - data
  - projection
  - DWD
authors:
  - name: Thomas Ramsauer
    orcid: 0000-0001-5322-4540
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Ludwig-Maximilians-Universität München, Department for Geography
   index: 1
date: 25 October 2019
bibliography: paper.bib
---

# Summary

<!-- The software should be open source as per the OSI definition. -->
<!--     The software should have an obvious research application. -->
<!--     You should be a major contributor to the software you are submitting. -->
<!--     The software should be a significant contribution to the available open source software that either enables some new research challenges to be addressed or makes addressing research challenges significantly better (e.g., faster, easier, simpler). -->
<!--     The software should be feature-complete (no half-baked solutions) and designed for maintainable extension (not one-off modifications). Minor ‘utility’ packages, including ‘thin’ API clients, are not acceptable. -->
<!--     Your paper (paper.md and BibTeX files, plus any figures) must be hosted in a Git-based repository, ideally together with your software. -->

Precipitation is of paramount importance when studying the water cycle which in turn drives the global climate and climate change.
Good knowledge on the parts of this mass and energy system is much needed to study different events, e.g. droughts, that may impact humans in their daily life.
For example soil moisture and land cover and therefore agriculture hence food production is highly dependent on rainfall.
Science on hydroclimatic extremes investigates atmospheric conditions which may lead to devastating flooding events.
Accurate input to improve hydrological model setups is a necessity for such scientific groups.
Also, general climate modeling requires precise precipitation data to validate against.
However, hydrological modeling communities struggle to get reliable data for this essential climate valiable (ECV). **SOURCE**

There are several measuring methods for precipitation with the most prominent in society being traditionl gauge data.
Point scale data inherits limited informative value for nearby areas (kilometers) which is a big drawback for to hydrological applications.
A spatial representative precipitation data set is thus required.
In the last decades satellite missions where launched to measure precipitation from space.
These data sets come with peculiar uncertainties (e.g. winter) and resolutions up to .1° / ~10 km (Global Precipitation Measurement Mission). **SOURCE**
Weather radars also provide areal representations of the rainfall around the station's location and can deliver data at a high sampling rate and spatial resolution.

RADOLAN is the German weather radar system operated by the Deutscher Wetterdienst (DWD).
It is a gauge adjusted precipitation data set with spatial, temporal and radiometric resolution of 1 km, 1 hourly, .1 mm/h respectively.
The data set is utilized in several studies already. **SOUCE**

However, a DWD inherent geographic #############

## Goal of software
The overall goal of the software is to make the RADOLAN data set more accessible to users. A short investigation of single dates e.g. for flooding antecedent precipitation situation is easily possible with ``raddo``.

## Software description
``raddo`` is a Python package for retrieval and preprocessing of RADOLAN weather radar data and the name stands for RADolan DOwnload and preprocessing software.
**KREKLOW**

The software operates in several steps which can be accessed through the commandline interface.
The first step is to make a local list of potentially to load data sets. This is done to elleviate DWD's server from too many requests and is also based on difficulties in reaching the data store of RADOLAN data.
Next, the data is sorted, untarred or gunzipped depending on dataset.
Finally, ...

3 reproject aggregate

[@Binney:2008]



# Acknowledgements

We acknowledge DWD for openly providing the RADOLAN data free of charge under the following url:

# References


<!-- -------------------------------------------- -->


# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$


# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this: ![Example figure.](figure.png)
