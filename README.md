---
title: deep_research
app_file: app.py
sdk: gradio
sdk_version: 6.14.0
---

# Deep Research

Deep Research is a local web app that turns a research question into a written
report with source links. Enter a topic, click **Investigate**, and the app plans
several searches, collects web results, summarizes the findings, and combines
them into a report. It is useful for getting an initial overview of a topic,
comparing approaches, or identifying sources to investigate further.

The interface is built with Gradio, and the workflow uses the OpenAI Agents SDK
to coordinate specialized agents. In the default configuration, all model calls
use **`gpt-5.6-luna` through Experiential Labs**, while **Serper** supplies web
search results. An OpenAI API key is not required for this configuration, and
OpenAI tracing is disabled.

## How it works

1. **Plan the research.** The planner turns your question into a set of focused
   search queries, each with a reason for searching. It is instructed to produce
   five queries by default.
2. **Search the web.** The app runs the planned searches concurrently through
   Serper, requesting five results per query. It collects titles, URLs, and
   snippets from the organic search results.
3. **Summarize the evidence.** A search agent summarizes each result set in
   two or three paragraphs, retaining source links and using the supplied
   evidence.
4. **Write the report.** The writer combines the summaries with your original
   question. It is instructed to produce a report of approximately 800–1,200
   words, cite sources, and acknowledge gaps in the evidence.
5. **Display the result.** The page shows progress messages during the run and
   then displays the final Markdown report. Optional email or push delivery
   can be enabled separately.

The writer also generates a short summary and suggested follow-up questions as
structured data internally. The current interface displays the report itself;
it does not show those fields separately.

## Run locally

Run these commands from the **repository root**. If the repository already has
an environment with this app's dependencies installed, skip the first two steps.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Add the following to the repository's `.env` file, or set the variables in the
shell where you start the app. Replace the placeholders with your credentials;
do not commit API keys.

```dotenv
EXPLABS_API_KEY=your_experiential_labs_api_key
SERPER_API_KEY=your_serper_api_key
```

Start the app:

```bash
.venv/bin/python app.py
```

Open **http://127.0.0.1:7860**, type a question, and click **Investigate** or press
Enter. For example:

> How do solar panels generate electricity, and what limits their efficiency?

Keep the terminal running while using the app. Press `Ctrl+C` to stop it.
The server binds to `127.0.0.1`, so it is accessible on your own computer.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `EXPLABS_API_KEY` | Required | Authenticates model requests to Experiential Labs. |
| `SERPER_API_KEY` | Required | Authenticates web searches through Serper. |
| `DEEP_RESEARCH_MODEL` | `gpt-5.6-luna` | Model used by the research agents. |
| `DEEP_RESEARCH_PROVIDER` | `explabs` | Selects the model provider. |
| `HOW_MANY_SEARCHES` | `5` | Number of searches requested from the planner. Use a positive integer. |
| `PORT` | `7860` | Port used by the local web interface. |
| `DEEP_RESEARCH_SEND_EMAIL` | `false` | Enables optional report delivery when set to `true`. |

The default model endpoint is
`https://api.experientiallabs.ai/v1/chat/completions`.
The app's model settings are separate from the repository-wide `MODEL_PROVIDER`
and `DEFAULT_MODEL_NAME` variables. Restart the server after changing settings.

The model helper also supports `openai`, `gemini`, `openrouter`, and `groq`.
When changing providers, set both `DEEP_RESEARCH_PROVIDER` and
`DEEP_RESEARCH_MODEL`, along with that provider's API key. The selected model
must support the structured outputs used by the planner and writer. Web search
continues to use Serper regardless of the model provider.

## Deploy on Render

For the standalone `deep_research` repository, use a Python web service with:

- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Branch: `main`

In the service's Environment settings, add `EXPLABS_API_KEY` and
`SERPER_API_KEY`. Set `DEEP_RESEARCH_PROVIDER=explabs` and
`DEEP_RESEARCH_MODEL=gpt-5.6-luna` if overriding existing values. Leave
`DEEP_RESEARCH_SEND_EMAIL=false` unless report delivery is configured.
Local shell variables and `.env` files are not automatically copied to Render.

The app detects Render's `RENDER=true` environment variable and binds to
`0.0.0.0`, using Render's `PORT`. Local runs continue to use `127.0.0.1`.
Save the environment settings and deploy the latest commit. With automatic
deploys enabled for the linked branch, future pushes trigger a deployment.

## Optional report delivery

Reports are displayed locally by default. To enable delivery after report
creation, set `DEEP_RESEARCH_SEND_EMAIL=true`.

- **Email:** Leave `USE_EMAIL=true` (the default) and configure `EMAIL_ADDRESS`,
  `EMAIL_SMTP_SERVER`, and `EMAIL_APP_PASSWORD`. The app connects to SMTP on port
  587 with STARTTLS and sends the report to the configured `EMAIL_ADDRESS`,
  which is also used as the sender.
- **Pushover:** Set `USE_EMAIL=false` and configure `PUSHOVER_USER` and
  `PUSHOVER_TOKEN` to send a push message instead.

With delivery enabled, that step runs before the final report appears in the
interface. A delivery error can therefore prevent the report from being shown.

## Project structure

| File | Responsibility |
| --- | --- |
| `app.py` | Gradio interface and research event handlers. |
| `research_manager.py` | Coordinates planning, concurrent searches, writing, and optional delivery. |
| `planner_agent.py` | Defines search planning instructions and the search-plan schema. |
| `search_agent.py` | Calls Serper and summarizes the returned search evidence. |
| `writer_agent.py` | Defines report-writing instructions and the report schema. |
| `model_utils.py` | Configures model providers, API clients, and model selection. |
| `email_agent.py` | Prepares report delivery through an agent tool. |
| `messenger.py` | Implements SMTP email and Pushover requests. |
| `styles.py` | Interface styling, header, and example questions. |
| `requirements.txt` | Python dependencies for this app. |

## Limitations and troubleshooting

- **Search evidence is limited to snippets.** The app does not download or read
  full articles. Source links help you check the underlying material, but a
  generated citation is not proof that every claim is correct.
- **Reports may take several minutes.** Search calls run concurrently, but
  planning and report writing happen in sequence. Speed depends on the model
  provider and the amount of research requested.
- **Local hosting still uses external APIs.** Research prompts and summaries are
  sent to the configured model provider, and search queries are sent to Serper.
  Usage draws on those accounts' quotas and may incur charges.
- **Reports are not automatically saved to disk.** Copy the result if you want
  to keep it. The app does not provide a report-history database.
- **Missing key or authentication error:** Check the relevant API key in the
  server's environment or repository `.env`, then restart the app.
- **Model or structured-output error:** Confirm that the selected model is
  available through your provider and supports the requested response format.
- **Search failure:** Check Serper credentials and available quota. A failed
  search can stop the current research run; partial-result recovery is not
  implemented.
- **Port already in use:** Stop the existing server or set a different `PORT`.
- **Other failures:** Check the terminal running the server for the underlying
  exception. The interface does not currently provide custom error recovery.
