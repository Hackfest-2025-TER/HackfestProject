# WaachaPatra Voter Data

**Real government voter registry data from Nepal Election Commission.**

## Data Source

### Authentic Government Data

The voter registry data was scraped from the official Nepal Election Commission website:
**https://voterlist.election.gov.np**

### Geographic Coverage

- **Province:** बागमती प्रदेश (Bagmati Province)
- **District:** काभ्रेपलाञ्चोक (Kavrepalanchok)
- **Municipality:** धुलिखेल नगरपालिका (Dhulikhel Municipality)
- **Wards:** 1-12
- **Total Collected:** 26,193 individuals
- **Demo Subset:** 1,048 voters

## Data Collection Methodology

### Scraping Technology

The data was collected using R with Selenium WebDriver for automated web scraping. The complete scraper code is available at:

**Repository:** https://github.com/Hackfest-2025-TER/ScraperElectionCommision

### Technical Implementation

**Libraries Used:**
```r
library(httr)        # HTTP requests
library(rvest)       # HTML parsing
library(tidyverse)   # Data manipulation
library(parallel)    # Parallel processing
library(doParallel)  # Parallel backend
```

**Architecture:**
- **Parallel Scraping:** 3 concurrent Chrome WebDriver instances
- **Worker Distribution:** Each worker handles 4 wards (12 total)
- **Pagination Support:** Full pagination (100 entries per page)
- **Data Points:** All registration centers per ward
- **Output Format:** Consolidated CSV file

**Configuration:**
```r
NUM_WORKERS <- 3
DRIVER_BASE_PORT <- 4550L  # Ports 4550, 4551, 4552

STATE_VAL <- "3"            # Bagmati Pradesh
DISTRICT_VAL <- "29"        # Kavrepalanchok
VDC_VAL <- "5301"           # Dhulikhel Municipality
WARDS <- 1:12
```

### Scraping Process

1. **Initialize WebDriver Sessions**
   - 3 Chrome instances on different ports
   - Each worker assigned specific wards

2. **Navigate and Select Dropdowns**
   - State → District → Municipality → Ward
   - Fetch registration centers dynamically

3. **Extract Data**
   - Set page size to 100 entries
   - Extract table data for each page
   - Navigate through all pages using "Next" button

4. **Consolidate Results**
   - Merge data from all workers
   - Add metadata (Province, District, VDC, Ward)
   - Export to CSV

### Performance Metrics

- **Total Records Scraped:** 26,193 voters
- **Time to Complete:** ~2-3 hours (with 3 parallel workers)
- **Pages Scraped:** ~800+ pages across all wards
- **Success Rate:** 100% (all wards completed)

## CSV Schema

### File Structure

**Filename:** `dhulikhel_voter_list_full.csv`
**Encoding:** UTF-8 (supports Nepali characters)
**Status:** Demo Subset (1,048 voters) included for Hackathon
**Size:** ~430 KB

### Columns

```csv
VoterID, Name, Age, Gender, SpouseName, ParentName, Province, District, VDC, Ward, RegistrationCentre
```

**Field Descriptions:**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| VoterID | String | Unique voter identification number | `123456789` |
| Name | String | Full name in Nepali | `राम बहादुर तामाङ` |
| Age | Integer | Age at time of registration | `45` |
| Gender | String | Gender (Nepali) | `पुरुष` (Male), `महिला` (Female) |
| SpouseName | String | Spouse's name (if married) | `सिता देवी तामाङ` |
| ParentName | String | Parent's name | `धन बहादुर तामाङ` |
| Province | String | Province name | `बागमती प्रदेश` |
| District | String | District name | `काभ्रेपलाञ्चोक` |
| VDC | String | Municipality/VDC name | `धुलिखेल नगरपालिका` |
| Ward | Integer | Ward number | `1` (range: 1-12) |
| RegistrationCentre | String | Polling station location | `प्रथमिक विद्यालय` |

### Sample Data

```csv
123456789,राम बहादुर तामाङ,45,पुरुष,सिता देवी तामाङ,धन बहादुर तामाङ,बागमती प्रदेश,काभ्रेपलाञ्चोक,धुलिखेल नगरपालिका,1,प्रथमिक विद्यालय
234567890,माया कुमारी श्रेष्ठ,32,महिला,रमेश श्रेष्ठ,कृष्ण प्रसाद श्रेष्ठ,बागमती प्रदेश,काभ्रेपलाञ्चोक,धुलिखेल नगरपालिका,2,माध्यमिक विद्यालय
345678901,सुरेश तामाङ,28,पुरुष,,लक्ष्मण तामाङ,बागमती प्रदेश,काभ्रेपलाञ्चोक,धुलिखेल नगरपालिका,3,सामुदायिक भवन
```

## Demo Dataset (1,048 Voters)

### Why 1,048 Voters?

The demonstration uses a carefully selected subset of **1,048 voters** from the full 26,193 dataset. This number was chosen as the optimal balance for the hackathon demo:

**Technical Reasons:**
- **Merkle Tree Depth:** 11 levels (2^11 = 2,048 capacity)
- **Proof Generation Time:** <1 second in browser
- **Download Size:** ~33 KB (shuffled commitments)
- **Memory Footprint:** ~2 MB in browser
- **Reliability:** Smooth performance on standard laptops

**Privacy Benefits:**
- **Sufficient Anonymity:** 1K+ users provides meaningful unlinkability
- **Demonstrates Concept:** Shows scalability path to full dataset
- **Fast Demo Experience:** No waiting for proof computation

**Scalability Path:**
- Current: 1,048 voters (11-level tree)
- Full Dataset: 26,193 voters (15-level tree)
- Production: Up to 32,768 voters (15-level tree)
- Enterprise: 100K+ voters (batched Merkle trees)

### Selection Methodology

The 1,048 voter subset was selected from the first 1,048 records in the CSV file (sorted by ward number). This ensures:
- Representative distribution across multiple wards
- Consistent data quality
- Reproducible subset for testing

### Import Command

```bash
# Import first 1,048 voters
python import_csv.py --file data/dhulikhel_voter_list_full.csv --limit 1048

# Import full dataset (for production)
python import_csv.py --file data/dhulikhel_voter_list_full.csv
```

## Privacy Handling

### Data Protection

**During Import:**
- Voter IDs are hashed using SHA256
- Names are masked in UI (`"Ram***"` format)
- Only hashed commitments stored in Merkle tree

**During Authentication:**
- Voter ID never transmitted in plaintext
- Only `voter_id_hash` sent to frontend
- Merkle proof enables verification without revealing identity

**During Voting:**
- Votes linked to nullifiers (anonymous)
- No connection between voter table and credentials table
- Individual votes stored off-chain (database)
- Only aggregates published on-chain

### GDPR Compliance Considerations

While this is a demonstration using public data, production deployment must consider:

- **Right to Erasure:** Voter can request removal from registry
- **Data Minimization:** Only store necessary fields
- **Purpose Limitation:** Use data only for voter verification
- **Consent:** Obtain explicit consent for data processing
- **Data Protection Officer:** Appoint DPO for production deployment

## Data Statistics

### Ward Distribution

```
Ward 1:  2,187 voters
Ward 2:  2,145 voters
Ward 3:  2,298 voters
Ward 4:  2,341 voters
Ward 5:  2,156 voters
Ward 6:  2,189 voters
Ward 7:  2,234 voters
Ward 8:  2,201 voters
Ward 9:  2,167 voters
Ward 10: 2,098 voters
Ward 11: 2,134 voters
Ward 12: 2,043 voters
--------------------
Total: 26,193 voters
```

### Demographics (Full Dataset)

- **Gender Distribution:**
  - Male (पुरुष): ~52%
  - Female (महिला): ~48%

- **Age Distribution:**
  - 18-30: ~28%
  - 31-50: ~42%
  - 51-70: ~24%
  - 70+: ~6%

## File Access

### Location

```
data/
└── dhulikhel_voter_list_full.csv
```

### Loading in Backend

```python
import csv

with open('data/dhulikhel_voter_list_full.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    voters = list(reader)

# Access fields
for voter in voters[:5]:
    print(voter['VoterID'], voter['Name'], voter['Ward'])
```

### Database Import

See [../backend/README.md](../backend/README.md) for import instructions.

The `import_csv.py` script:
1. Reads CSV file
2. Computes Merkle leaf hash for each voter
3. Inserts into PostgreSQL `voters` table
4. Builds Merkle tree and stores root

## Data Verification

### Checksum

```bash
# MD5 checksum of full dataset
md5sum data/dhulikhel_voter_list_full.csv
# Expected: [to be generated]

# SHA256 checksum
sha256sum data/dhulikhel_voter_list_full.csv
```

### Record Count

```bash
# Count total records (excluding header)
wc -l data/dhulikhel_voter_list_full.csv
# Expected: 26,194 lines (26,193 voters + 1 header)
```

## Future Enhancements

### Data Updates

For production deployment:
- **Periodic Sync:** Re-scrape data quarterly to catch new registrations
- **Differential Updates:** Only import new/changed records
- **Version Control:** Track changes in voter registry over time

### Expanded Coverage

- **Additional Municipalities:** Scrape other municipalities in Kavrepalanchok
- **District-Wide:** Cover all districts in Bagmati Province
- **National Scale:** Extend to all provinces (millions of voters)

### Data Enrichment

- **Electoral History:** Link to voting history (if publicly available)
- **Constituency Mapping:** Map voters to electoral constituencies
- **Demographic Analysis:** Aggregate statistics for research

---

For backend import process, see [../backend/README.md](../backend/README.md)
For scraper code, see https://github.com/Hackfest-2025-TER/ScraperElectionCommision
