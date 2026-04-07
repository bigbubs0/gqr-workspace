# Recruiter Candidate Intake Tool

A custom web-based tool for biotech/pharma executive recruiters to automate candidate intake processing from interview transcripts.

## Features

- **AI-Powered Extraction**: Automatically extracts structured candidate information from RingCentral transcripts or interview notes
- **Formatted Candidate Briefs**: Generates email-ready candidate summaries in your preferred format
- **Searchable Database**: Store and filter candidates by therapeutic area, phase experience, company, and custom search tags
- **Batch Export**: Export multiple candidates at once based on filter criteria
- **Local Storage**: All data stored locally in SQLite database
- **Local Telemetry**: Writes redacted JSONL traces for latency, token usage, retries, validation, and cost under `telemetry/`

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd "C:\Users\BryanBlair\OneDrive - GQR Global Markets\recruiter-tool"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment:**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Open `.env` in a text editor and set the values:
     ```
      OPENAI_API_KEY=sk-your-actual-api-key-here
      OPENAI_MODEL=gpt-5.4
      OPENAI_REASONING_EFFORT=medium
      TELEMETRY_ENABLED=true
      TELEMETRY_DIR=telemetry
      TELEMETRY_LOG_RAW_PROMPTS=false
     ```

### Running the Application

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

3. **You're ready to process candidates!**

## How to Use

### Processing a New Candidate

1. Go to the "Process New Candidate" tab
2. Paste your RingCentral transcript or interview notes into the text box
3. (Optional) Add search tags like "Aditum VP" or "Alkermes Med Dir" to associate this candidate with specific searches
4. Click "Process Candidate"
5. The AI will extract all relevant information and generate a formatted candidate brief
6. Click "Copy to Clipboard" to copy the brief for pasting into emails or your CRM

### Searching Your Database

1. Go to the "Search Database" tab
2. Enter filter criteria:
   - **Therapeutic Area**: e.g., "oncology", "rare disease"
   - **Phase**: e.g., "Phase 2", "Phase 3"
   - **Company**: e.g., "Amgen", "Genentech"
   - **Search Tag**: e.g., "Aditum VP"
   - **Days Back**: e.g., "14" (candidates from last 14 days)
3. Click "Search"
4. Click on any candidate card to view their full brief
5. Use "Export Results" to generate a combined document of all filtered candidates

## What Gets Extracted

The AI automatically identifies and structures:

- **Basic Info**: Name, current company, title
- **Experience**: Total years, therapeutic area experience
- **Technical Skills**: IND filings, clinical trial phases, therapeutic areas
- **Compensation**: Current and target ranges (both min/max captured)
- **Availability**: Notice period, location, relocation preferences
- **Red Flags**: Job hopping (jobs < 1 year), compliance issues, unrealistic expectations
- **Why Interesting**: 3-sentence narrative focusing on clinical development experience

## Auto-Detected Highlights

The AI is trained to recognize and highlight:

- Big Pharma → Biotech transitions
- Power companies: Amgen, Genentech, BMS, Pfizer, Regeneron, Vertex, Gilead
- Phase progression expertise (especially Phase 2+)
- Therapeutic area depth
- Regulatory experience (FDA meetings, IND filings, breakthrough designations)
- Team building from scratch

## Data Storage

- All candidate data is stored in `data/candidates.db` (SQLite database)
- Database is created automatically on first run
- Data is stored locally on your machine

## Telemetry

- Request and stage spans are written to `telemetry/custom-spans.ndjson`
- One-line request summaries are written to `telemetry/run-summaries.ndjson`
- Redacted errors are written to `telemetry/errors.ndjson`
- Raw transcripts, prompts, and generated briefs are not exported to telemetry
- To generate Chrome Trace JSON from saved spans:
  ```bash
  python export_chrome_trace.py
  ```

## Future Enhancements (Phase 2)

Once you've tested the basic prototype, we can add:

- Audio file upload with automatic transcription (Whisper API)
- Google Drive integration for backup
- Job requisition matching
- Layoff data cross-referencing for red flag validation
- Advanced analytics dashboard
- CRM integration (HubSpot, etc.)

## Troubleshooting

**"Module not found" error:**
- Run `pip install -r requirements.txt` again

**"OpenAI API error":**
- Check that your `.env` file has a valid API key
- Ensure you have credits in your OpenAI account

**"Port already in use":**
- Another application is using port 5000
- Stop the other application or change the port in `app.py` (last line)

## Cost Estimates

Using GPT-5.4 for extraction:
- Average cost per candidate depends on transcript length, output length, and cache reuse
- 50 candidates/month = ~$1-2.50/month in API costs

Very affordable for the automation value provided.

## Support

For questions or issues, contact your development team or refer to:
- OpenAI API Docs: https://platform.openai.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
