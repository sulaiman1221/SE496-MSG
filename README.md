MSG   Military Scenario Generator
A system that generates bilingual tactical military training scenarios using a large language model. this is our SE496 capstone project at Alfaisal University, spring 2026

What it does
Instructors fill out a short form describing a mission type, environment, available aircraft, friendly forces, enemy threat level and the system produces five distinct scenario variants in both English and Arabic. Each variant includes objectives, a phased timeline, rules of engagement, decision points, friendly and opposing forces, and evaluation metrics.

Past scenarios are saved to a database and can be reviewed, filtered, and reopened from a history page.

How it works
The backend runs a four agent pipeline over a single OpenAI gpt4o model:

Planner turns the instructor's input into five variant seeds.
Variant agents (run in parallel) elaborate each seed into a complete English scenario.
Translator agents render each scenario into Modern Standard Arabic.
Validator agents check structural parity and doctrinal plausibility before the result is saved.
The frontend is a React single-page application with full right-to-left support for Arabic.

Stack
Backend: Python , FastAPI, Pydantic, OpenAI SDK, Supabase
Frontend: React, Vite, TypeScript, Tailwind CSS, Premium components from Framer
Database: Supabase 



ROLES: \n Related work/Market research/Dataset: Fayez\n
Implementation/Testing: Abdullah/Sulaiman\n
Security and data privacy: Saleh\n
Ethical and social impact/Conclusion/Future work : Naif
