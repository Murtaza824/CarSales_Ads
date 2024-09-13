# Payer-Data-Analysis and Calculator

https://payer-data-analysis.onrender.com/

## Overview
This app allows you to explore healthcare payer data across the U.S. You can calculate the price of a service based on the negotiated rate for a given payer, provider, and state. Further below, you can filter and play around with the data across different dimensions.


This web data application is powered by a dataset provided by Turquoise Health, a company trying to bring price transparency to the healthcare industry (also check out www.superscript.nyc for anyone looking for a truly innovative solution to healthcare price transparency).

As we all know today, healthcare pricing is broken. So I took this dataset which revolves specifically around payers (healthcare providers, Medicaid, Medicare, etc.) and what their in-network negotiated rates are with all the provider and doctor groups they have partnered with. I've broken this dataset so it can be filterable across a few parameter, visualized a few important cases within the data so it's easier to understand, and lastly, I built a pricing calculator which should give a rough estimate of how much a visit would cost based on a few parameters.

## Launching it locally
Clone this repo and make sure you have streamlit, numpy, pandas, altair, matplotlib.pyplot, and plotly.express installed on your computer.

In order to run the application, type in "streamlit run main.py"
