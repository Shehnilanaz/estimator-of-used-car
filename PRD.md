# PRD — Used-Car Price Estimator

## The problem

When you shop for a used car, every seller asks a different price for the same car, and there's no quick way to know what's fair. Existing valuation tools are built for dealers, hidden behind sign-ups, or don't explain where the number comes from. A buyer looking at a listing needs a fast, honest answer: is this price reasonable?

## Who it's for

- Everyday shoppers comparing a used-car listing before they buy or negotiate
- Small sellers checking that their asking price is realistic

## Goals

- Estimate a fair price in seconds, from real used-car listings rather than gut feel
- Run in the browser with no account or download for the user
- Explain the answer in plain English, so the user can trust it or question it
- Stay simple enough that one person can maintain it

## In scope (v1)

- Inputs: brand, model, year, mileage, fuel type, transmission
- Output: one fair-price estimate in USD, learned from `used-cars.csv` (3,915 real listings)
- Runs locally in a browser now; deployable to a public URL later

## Out of scope (v1)

- Live market data or dealer APIs beyond our dataset
- Accident or clean-title history as inputs (possible stretch goal)
- Accounts, saved cars, or price history
- Financing, trade-in value, or taxes and fees
- Being a formal appraisal — this is a guide, not a guarantee

## How we'll know it works

- Sanity checks pass: newer and lower mileage = higher estimate; the same car with 50,000 more miles = lower estimate
- Estimates land near real listings for the same model and year
- A first-time user gets an answer in under a minute, without instructions
