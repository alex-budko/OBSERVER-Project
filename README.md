# Synthetic Doctor Messages Generator

This project uses OpenAI's GPT-4 model to generate synthetic doctor messages based on patients' responses. The goal is to simulate doctor-patient conversations by applying a "chain of thought" (CoT) approach to each patient's message.

## Getting Started

These instructions will guide you on how to run the code.

### Prerequisites

Make sure you have the following installed on your system:

- Python 3.7 or later
- `openai` Python package
- `pandas` Python package
- `scikit-learn` Python package

You can install the packages using pip.

### Setup

Create a `.env` file in the root directory of your project. This file should include:

- API_KEY: specifies OpenAI API Key
- MODEL: specifies model, i.e. gpt-3.5-turbo