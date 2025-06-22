# 🚀 Complete Postman Setup Guide - PDF Industrial Pipeline API

*This is your comprehensive guide to setting up and automating API testing in Postman*

## 📋 Table of Contents
1. [Initial Setup & Environment](#1-initial-setup--environment)
2. [Collection Setup with Automation](#2-collection-setup-with-automation)
3. [Endpoint Configurations](#3-endpoint-configurations)
4. [Complete Automated Workflow](#4-complete-automated-workflow)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Initial Setup & Environment

### 🌐 Create Environment
**Step 1:** Click the **"Environments"** tab (gear icon in left sidebar)  
**Step 2:** Click **"Create Environment"**  
**Step 3:** Name it: `PDF Pipeline Local`  
**Step 4:** Add these variables:

| Variable Name | Initial Value | Current Value | Description |
|---------------|---------------|---------------|-------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` | API server URL |
| `job_id` | `` | `` | Current job ID (auto-updated) |
| `current_filename` | `` | `` | Uploaded file name |
| `page_count` | `` | `` | Number of pages processed |

**Step 5:** Click **"Save"**  
**Step 6:** **Select this environment** from dropdown in top-right corner

### 📁 Create Collection
**Step 1:** Click **"Collections"** tab  
**Step 2:** Click **"Create Collection"**  
**Step 3:** Name: `PDF Industrial Pipeline`  
**Step 4:** Description: `Complete API testing suite with automation`  
**Step 5:** Click **"Save"**

### ⚙️ Collection-Level Automation Setup
**Step 1:** Right-click your collection → **"Edit"**  
**Step 2:** Go to **"Tests"** tab  
**Step 3:** Add this global automation script:

```javascript
// ===== GLOBAL AUTOMATION SCRIPT =====
// This runs after EVERY request in the collection

console.log("=== RESPONSE INFO ===");
console.log("Status:", pm.response.code);
console.log("Time:", pm.response.responseTime + "ms");

// Auto-save important data from ANY response
if (pm.response.code < 400) {
    try {
        const responseData = pm.response.json();
        
        // Auto-extract job_id from any response
        if (responseData.job_id) {
            pm.environment.set("job_id", responseData.job_id);
            console.log("🔄 Auto-saved job_id:", responseData.job_id);
        }
        
        // Auto-extract other useful data
        if (responseData.original_filename) {
            pm.environment.set("current_filename", responseData.original_filename);
        }
        
        if (responseData.page_count) {
            pm.environment.set("page_count", responseData.page_count);
        }
        
    } catch (e) {
        // Non-JSON response is fine
    }
}

// Error handling
if (pm.response.code >= 400) {
    console.log("❌ ERROR:", pm.response.text());
}
```

---

## 2. Endpoint Configurations

### 🏥 1. Health Check

**Create new request:**
- **Name**: `01 - Health Check`
- **Method**: `GET`
- **URL**: `{{base_url}}/health`

**Tests script:**
```javascript
pm.test("Server is healthy", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    pm.expect(response.status).to.eql("healthy");
    
    console.log("📊 System Health:");
    Object.keys(response.checks).forEach(check => {
        console.log(`  ${check}: ${response.checks[check] ? '✅' : '❌'}`);
    });
});
```

---

### 📤 2. File Upload (MOST IMPORTANT)

**Create new request:**
- **Name**: `02 - Upload PDF File` 
- **Method**: `POST`
- **URL**: `{{base_url}}/upload`

#### 🔧 Body Setup (CRITICAL STEPS):

**Step 1:** Click **"Body"** tab  
**Step 2:** Select **"form-data"** radio button (NOT x-www-form-urlencoded!)  
**Step 3:** Add ONE row only:

```
Key: file
Type: [Dropdown] File ← MUST select "File" not "Text"
Value: [Click "Select Files"] → Choose your PDF
```

**Visual Guide:**
```
Body Options:
• none             ⭕
• form-data        ✅ ← SELECT THIS
• x-www-form-url.. ⭕  
• raw              ⭕
• binary           ⭕

Form Data Table:
┌─────┬──────┬─────────────┐
│ Key │ Type │ Value       │
├─────┼──────┼─────────────┤
│file │File ▼│Select Files │ ← Type MUST be "File"
└─────┴──────┴─────────────┘
```

**⚠️ Common Mistakes:**
- ❌ Setting Type to "Text" instead of "File"
- ❌ Adding multiple rows
- ❌ Manually setting Content-Type header

**Tests script:**
```javascript
pm.test("File uploaded successfully", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    // Validate response
    pm.expect(response).to.have.property("job_id");
    pm.expect(response.job_id).to.match(/^[0-9a-f-]{36}$/); // UUID format
    
    // Auto-save EVERYTHING for next requests
    pm.environment.set("job_id", response.job_id);
    pm.environment.set("current_filename", response.original_filename);
    pm.environment.set("page_count", response.page_count);
    pm.environment.set("output_directory", response.output_directory);
    
    // Success logging
    console.log("🎉 UPLOAD SUCCESS!");
    console.log("📁 File:", response.original_filename);
    console.log("📄 Pages:", response.page_count);
    console.log("🆔 Job ID:", response.job_id);
    console.log("📂 Directory:", response.output_directory);
});
```

---

### 📊 3. Job Status Check

**Create new request:**
- **Name**: `03 - Check Job Status`
- **Method**: `GET`  
- **URL**: `{{base_url}}/job/{{job_id}}/status`

#### 🔍 Understanding Path Variables:

**What you see:** `{{base_url}}/job/{{job_id}}/status`  
**What Postman does:**
1. Sees `{{job_id}}`
2. Looks up "job_id" in environment variables
3. Replaces with actual value: `http://localhost:8000/job/abc-123-def/status`

**Pre-request Script:**
```javascript
// Verify we have a job_id before sending request
const jobId = pm.environment.get("job_id");
if (!jobId) {
    throw new Error("❌ No job_id! Run the Upload request first.");
}
console.log("🔍 Checking status for job:", jobId);
```

**Tests script:**
```javascript
pm.test("Job status retrieved", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("📋 JOB STATUS:");
    console.log("  Status:", response.status || "unknown");
    console.log("  Progress:", response.progress || "N/A");
    
    if (response.error) {
        console.log("❌ Error:", response.error);
    }
});
```

---

### 📋 4. Job Manifest

**Create new request:**
- **Name**: `04 - Get Job Manifest`
- **Method**: `GET`
- **URL**: `{{base_url}}/job/{{job_id}}/manifest`

**Tests script:**
```javascript
pm.test("Manifest retrieved", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("📄 MANIFEST:");
    console.log("  Pages:", response.pages ? response.pages.length : 0);
    console.log("  Metadata items:", response.metadata ? Object.keys(response.metadata).length : 0);
});
```

---

### 🧠 5. Text Processing

**Create new request:**
- **Name**: `05 - Process Text Analysis`
- **Method**: `POST`
- **URL**: `{{base_url}}/process-text/{{job_id}}`

**Headers:**
```
Content-Type: application/json
```

**Body:**
- Select **"raw"**
- Type: **JSON**
- Content: `{}`

**Tests script:**
```javascript
pm.test("Text processing successful", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🧠 TEXT ANALYSIS:");
    console.log("  Status:", response.status);
    
    if (response.result && response.result.entities) {
        console.log("  Entities found:", Object.keys(response.result.entities).length);
    }
    
    if (response.result && response.result.sentiment) {
        console.log("  Sentiment:", response.result.sentiment.label);
    }
});
```

---

### 🔗 6. Generate Embeddings

**Create new request:**
- **Name**: `06 - Generate Embeddings`
- **Method**: `POST`
- **URL**: `{{base_url}}/generate-embeddings/{{job_id}}`

**Headers:** `Content-Type: application/json`  
**Body:** Raw JSON: `{}`

**Tests script:**
```javascript
pm.test("Embeddings generated", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🔗 EMBEDDINGS:");
    console.log("  Status:", response.status);
    
    if (response.embeddings_info) {
        console.log("  Vectors:", response.embeddings_info.vector_count);
        console.log("  Dimensions:", response.embeddings_info.dimension);
    }
});
```

---

### 🤖 7. ML Feature Extraction

**Create new request:**
- **Name**: `07 - Extract ML Features`
- **Method**: `POST`
- **URL**: `{{base_url}}/extract-features/{{job_id}}`

**Headers:** `Content-Type: application/json`  
**Body:** Raw JSON: `{}`

**Tests script:**
```javascript
pm.test("ML features extracted", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🤖 ML FEATURES:");
    if (response.features) {
        Object.keys(response.features).forEach(category => {
            console.log(`  ${category}:`, response.features[category].length || 0, "items");
        });
    }
});
```

---

### 🎯 8. Lead Prediction

**Create new request:**
- **Name**: `08 - Predict Lead Quality`
- **Method**: `POST`  
- **URL**: `{{base_url}}/predict-leads/{{job_id}}`

**Headers:** `Content-Type: application/json`  
**Body:** Raw JSON: `{}`

**Tests script:**
```javascript
pm.test("Lead prediction successful", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🎯 LEAD PREDICTION:");
    
    if (response.predictions) {
        console.log("  Lead Score:", response.predictions.lead_score);
        console.log("  Confidence:", response.predictions.confidence);
        console.log("  Category:", response.predictions.category);
        
        // Auto-save lead score for later use
        if (response.predictions.lead_score) {
            pm.environment.set("lead_score", response.predictions.lead_score);
        }
    }
});
```

---

### 🔍 9. Semantic Search

**Create new request:**
- **Name**: `09 - Semantic Search`
- **Method**: `POST`
- **URL**: `{{base_url}}/search/semantic`

**Headers:** None required  
**Body:** None (select "none")

#### 🔧 Adding Query Parameters:

**Method 1 - URL Bar:**
```
{{base_url}}/search/semantic?query=technology companies with high revenue&k=10&threshold=0.7&job_id={{job_id}}
```

**Method 2 - Params Tab (Recommended):**
1. Click **"Params"** button next to URL
2. Add parameters:

| Key | Value | Description |
|-----|-------|-------------|
| `query` | `technology companies with high revenue` | Natural language search text |
| `k` | `10` | Number of results (1-50) |
| `threshold` | `0.7` | Similarity score (0.0-1.0, higher = more strict) |
| `job_id` | `{{job_id}}` | Search in specific job only (optional) |

**Visual Guide:**
```
URL: {{base_url}}/search/semantic
Params Tab:
┌───────────┬─────────────────────────────────────┬─────────────────────┐
│ Key       │ Value                               │ Description         │
├───────────┼─────────────────────────────────────┼─────────────────────┤
│ query     │ technology companies with high...   │ Search text         │
│ k         │ 10                                  │ Max results         │
│ threshold │ 0.7                                 │ Similarity score    │
│ job_id    │ {{job_id}}                          │ Filter by job       │
└───────────┴─────────────────────────────────────┴─────────────────────┘

Final URL: {{base_url}}/search/semantic?query=technology%20companies...
```

#### 📝 Parameter Guide:
- **query**: Natural language search (e.g., "urgent construction projects")
- **k**: Number of results (1-50)
- **threshold**: Similarity score (0.0-1.0, higher = more strict)
- **job_id**: Search in specific job only (optional)

**Tests script:**
```javascript
pm.test("Semantic search successful", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🔍 SEMANTIC SEARCH RESULTS:");
    console.log("  Query:", response.query_text);
    console.log("  Total Results:", response.total_results);
    console.log("  Model Used:", response.model_used);
    console.log("  Threshold Used:", response.threshold_used);
    
    if (response.results && response.results.length > 0) {
        console.log("  Top Result Similarity:", response.results[0].similarity);
        console.log("  Top Result Text:", response.results[0].text_preview);
        
        // Show top 3 results
        response.results.slice(0, 3).forEach((result, i) => {
            console.log(`  Result ${i+1}: Similarity ${result.similarity.toFixed(3)} - Job ${result.job_id} Page ${result.page_number}`);
        });
    } else {
        console.log("  No results found - try lowering threshold or different query");
    }
});
```

---

### 🏆 10. High-Score Leads

**Create new request:**
- **Name**: `10 - Get High-Score Leads`
- **Method**: `GET`
- **URL**: `{{base_url}}/search/leads`

#### 🔧 Adding Query Parameters:

**Method 1 - URL Bar:**
Add `?min_score=70.0` to URL: `{{base_url}}/search/leads?min_score=70.0`

**Method 2 - Params Tab (Recommended):**
1. Click **"Params"** button next to URL
2. Add parameter:

| Key | Value | Description |
|-----|-------|-------------|
| `min_score` | `70.0` | Minimum lead score (0-100) |

**Visual Guide:**
```
URL: {{base_url}}/search/leads
Params Tab:
┌───────────┬───────┬─────────────────────┐
│ Key       │ Value │ Description         │
├───────────┼───────┼─────────────────────┤
│ min_score │ 70.0  │ Min score threshold │
└───────────┴───────┴─────────────────────┘

Final URL: {{base_url}}/search/leads?min_score=70.0
```

**Tests script:**
```javascript
pm.test("High-score leads retrieved", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    
    console.log("🏆 HIGH-SCORE LEADS:");
    console.log("  Leads found:", response.leads ? response.leads.length : 0);
    
    if (response.leads && response.leads.length > 0) {
        console.log("  Highest score:", response.statistics?.highest_score);
        
        // Show top leads
        response.leads.slice(0, 3).forEach((lead, i) => {
            console.log(`  Lead ${i+1}: ${lead.company_name} (${lead.score})`);
        });
    }
});
```

---

### 🗑️ 11. Job Cleanup

**Create new request:**
- **Name**: `11 - Cleanup Job`
- **Method**: `DELETE`
- **URL**: `{{base_url}}/job/{{job_id}}`

**Tests script:**
```javascript
pm.test("Job cleanup successful", function () {
    pm.response.to.have.status(200);
    
    console.log("🗑️ CLEANUP COMPLETE");
    
    // Clear all job-related variables
    pm.environment.unset("job_id");
    pm.environment.unset("current_filename"); 
    pm.environment.unset("page_count");
    pm.environment.unset("output_directory");
    pm.environment.unset("lead_score");
    
    console.log("🧹 Environment variables cleared");
});
```

---

## 3. Complete Automated Workflow

### 🔄 Collection Runner Setup
1. **Click your collection name**
2. **Click "Run" button** 
3. **Select requests to run** (or all)
4. **Set delay**: `3000ms` (3 seconds between requests)
5. **Click "Run PDF Industrial Pipeline"**

### 🚀 One-Click Complete Pipeline

**Create a master request:**
- **Name**: `00 - Complete Automated Pipeline`
- **Method**: `POST`
- **URL**: `{{base_url}}/upload`
- **Body**: Same file upload setup as request #2

**Tests - Full Pipeline Automation:**
```javascript
// Stage 1: Upload file
pm.test("Stage 1: File Upload", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    pm.environment.set("job_id", response.job_id);
    console.log("✅ Stage 1 Complete - Job ID:", response.job_id);
});

// Auto-run entire pipeline
if (pm.response.code === 200) {
    const jobId = pm.response.json().job_id;
    const baseUrl = pm.environment.get("base_url");
    
    // Helper function to run next stage
    function runStage(url, stageName, callback) {
        setTimeout(() => {
            pm.sendRequest({
                url: url,
                method: 'POST',
                header: { 'Content-Type': 'application/json' },
                body: { mode: 'raw', raw: '{}' }
            }, (err, res) => {
                if (!err && res.code === 200) {
                    console.log(`✅ ${stageName} Complete`);
                    if (callback) callback();
                } else {
                    console.log(`❌ ${stageName} Failed:`, err || res.code);
                }
            });
        }, 2000); // 2 second delay between stages
    }
    
    // Stage 2: Text Processing
    runStage(`${baseUrl}/process-text/${jobId}`, "Stage 2: Text Processing", () => {
        
        // Stage 3: Generate Embeddings  
        runStage(`${baseUrl}/generate-embeddings/${jobId}`, "Stage 3: Embeddings", () => {
            
            // Stage 4: Extract Features
            runStage(`${baseUrl}/extract-features/${jobId}`, "Stage 4: ML Features", () => {
                
                // Stage 5: Predict Leads
                runStage(`${baseUrl}/predict-leads/${jobId}`, "Stage 5: Lead Prediction", () => {
                    console.log("🎉 COMPLETE PIPELINE SUCCESS! All 5 stages completed.");
                });
            });
        });
    });
}
```

---

## 4. Troubleshooting

### ❌ Common Issues & Solutions

#### **Issue 1: 422 Unprocessable Entity on Upload**
**Cause:** File field misconfigured  
**Solution:**
- ✅ Ensure Key type is **"File"** not "Text"  
- ✅ Use only ONE form-data row
- ✅ Don't set Content-Type header manually

#### **Issue 2: 404 Not Found with {{job_id}}**
**Cause:** job_id variable not set  
**Solution:**
1. Run upload request first
2. Check environment variables panel (eye icon)
3. Manually set job_id if auto-extraction failed

#### **Issue 3: Server Connection Refused**
**Cause:** Server not running  
**Solution:**
```bash
# In terminal:
python3 -m uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

#### **Issue 4: 422 Error on Semantic Search**
**Cause:** Using JSON body instead of query parameters  
**Solution:**
- ✅ Use **Params tab** not Body tab
- ✅ Set Body to **"none"**
- ✅ Add query, k, threshold, job_id as parameters
- ❌ Don't use JSON body format

#### **Issue 5: Path Variable Not Resolving**
**Cause:** Wrong variable name or environment not selected  
**Solution:**
1. Check environment is selected (top-right dropdown)
2. Verify variable name matches exactly: `job_id`
3. Check variable has a value in environment panel

### 🔧 Debug Helpers

**Add to any request's Pre-request Script for debugging:**
```javascript
console.log("=== DEBUG INFO ===");
console.log("Environment:", pm.environment.name);
console.log("Base URL:", pm.environment.get("base_url"));
console.log("Job ID:", pm.environment.get("job_id"));
console.log("Request URL:", pm.request.url.toString());

// List all environment variables
const allVars = pm.environment.toObject();
console.log("All Variables:", Object.keys(allVars));
```

### 📊 Variable Management Commands

```javascript
// Set variable
pm.environment.set("variable_name", "value");

// Get variable  
const value = pm.environment.get("variable_name");

// Remove variable
pm.environment.unset("variable_name");

// Check if variable exists
if (pm.environment.get("job_id")) {
    console.log("job_id exists");
}
```

---

## 5. Quick Start Checklist

**Setup Phase:**
- [ ] ✅ Create environment `PDF Pipeline Local`
- [ ] ✅ Add base_url variable: `http://localhost:8000` 
- [ ] ✅ Create collection `PDF Industrial Pipeline`
- [ ] ✅ Add global automation script to collection
- [ ] ✅ Select environment in top-right dropdown

**Testing Phase:**
- [ ] ✅ Test health endpoint first
- [ ] ✅ Upload PDF file (verify job_id auto-saved)
- [ ] ✅ Check job status
- [ ] ✅ Run text processing
- [ ] ✅ Generate embeddings
- [ ] ✅ Extract ML features
- [ ] ✅ Predict leads
- [ ] ✅ Test semantic search
- [ ] ✅ Check high-score leads
- [ ] ✅ Cleanup job when done

**Automation Phase:**
- [ ] ✅ Use Collection Runner for batch testing
- [ ] ✅ Try the complete automated pipeline request
- [ ] ✅ Verify all variables auto-update correctly

---

**🎉 Congratulations! Your Postman setup is now fully automated and professional-grade.**

**💡 Pro Tips:**
- Use the Console tab (bottom) to see all logging output
- Check the Tests tab results for each request
- Monitor the Environment panel to see variables updating
- Use Collection Runner for regression testing
- Export your collection to share with team members

**Need help?** Check server logs and Postman Console for detailed debugging information. 