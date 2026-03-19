/**
 * CV Auto-Sort
 * Google Drive Organization Project - Recurring Automation
 *
 * Runs every 15 minutes. Scans 00_INBOX for new CV files (PDF, DOC, DOCX,
 * and Google Docs converted from DOCX uploads), moves each to 01_CANDIDATES,
 * and fires the Make.com webhook so the CV Intake Pipeline v2 can download,
 * parse (GPT-4o), and push to Notion.
 *
 * DEPLOYMENT:
 * 1. Go to https://script.google.com
 * 2. Click "+ New project", name it "CV Auto-Sort"
 * 3. Delete default code, paste ALL of this
 * 4. Save (Ctrl+S)
 * 5. Select "installTrigger" from the function dropdown, click Run
 *    - First run: click "Review permissions" > choose your Google account > Allow
 * 6. Verify trigger appears in Triggers tab (clock icon, left sidebar)
 *
 * To run manually: select "processInbox" and click Run
 * To stop: delete the trigger from the Triggers tab
 */

// ==============================================
// CONFIGURATION
// ==============================================
var CONFIG = {
  INBOX_FOLDER_ID: '1tOJh8IPPhsKTa706Xk5cei6lA14DHVK_',       // 00_INBOX
  CANDIDATES_FOLDER_ID: '19p0p8_aZKRRhHjvjZSJXxIIzuOcFfOTk',  // 01_CANDIDATES
  WEBHOOK_URL: 'https://hook.us2.make.com/udk9t1w8hccv76rl6aea714fjauofuwn',

  // File types to process (lowercase extensions)
  CV_EXTENSIONS: ['pdf', 'doc', 'docx'],

  // MIME types to process (catches Google-converted files with no extension)
  CV_MIMETYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.document'
  ],

  // Max files per run to avoid timeout (Apps Script 6-min limit)
  BATCH_SIZE: 10,

  // Property key for tracking processed file IDs
  PROCESSED_KEY: 'cv_auto_sort_processed'
};

// ==============================================
// MAIN FUNCTION
// ==============================================
function processInbox() {
  Logger.log('=== CV Auto-Sort: STARTING ===');
  Logger.log('Timestamp: ' + new Date().toISOString());

  var inbox = DriveApp.getFolderById(CONFIG.INBOX_FOLDER_ID);
  var candidates = DriveApp.getFolderById(CONFIG.CANDIDATES_FOLDER_ID);
  var processed = getProcessedSet();
  var filesProcessed = 0;
  var errors = [];

  // Get all files in inbox
  var files = inbox.getFiles();

  while (files.hasNext() && filesProcessed < CONFIG.BATCH_SIZE) {
    var file = files.next();
    var fileId = file.getId();
    var fileName = file.getName();

    // Skip already-processed files (handles webhook retry scenarios)
    if (processed[fileId]) {
      Logger.log('SKIP (already processed): ' + fileName);
      continue;
    }

    // Check if file is a CV type (by extension OR mimeType)
    var ext = getExtension(fileName);
    var mime = file.getMimeType();
    if (CONFIG.CV_EXTENSIONS.indexOf(ext) === -1 && CONFIG.CV_MIMETYPES.indexOf(mime) === -1) {
      Logger.log('SKIP (not CV type): ' + fileName + ' [.' + ext + '] [' + mime + ']');
      continue;
    }

    Logger.log('PROCESSING: ' + fileName + ' (' + fileId + ')');

    try {
      // 1. Move file from 00_INBOX to 01_CANDIDATES
      file.moveTo(candidates);
      Logger.log('  Moved to 01_CANDIDATES');

      // 2. Fire Make.com webhook with file info
      var webhookSuccess = fireWebhook(fileId, fileName);

      if (webhookSuccess) {
        Logger.log('  Webhook fired successfully');
        markProcessed(fileId);
        filesProcessed++;
      } else {
        // Move file back to inbox if webhook failed
        file.moveTo(inbox);
        errors.push(fileName + ': webhook failed');
        Logger.log('  ERROR: webhook failed, moved back to inbox');
      }
    } catch (e) {
      errors.push(fileName + ': ' + e.message);
      Logger.log('  ERROR: ' + e.message);
    }
  }

  // Summary
  Logger.log('--- Summary ---');
  Logger.log('Files processed: ' + filesProcessed);
  Logger.log('Errors: ' + errors.length);
  if (errors.length > 0) {
    Logger.log('Error details: ' + errors.join('; '));
  }
  Logger.log('=== CV Auto-Sort: DONE ===');
}

// ==============================================
// WEBHOOK
// ==============================================
function fireWebhook(fileId, fileName) {
  var payload = {
    fileId: fileId,
    fileName: fileName,
    source: 'cv_auto_sort',
    timestamp: new Date().toISOString()
  };

  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(CONFIG.WEBHOOK_URL, options);
    var code = response.getResponseCode();
    if (code >= 200 && code < 300) {
      return true;
    } else {
      Logger.log('  Webhook HTTP ' + code + ': ' + response.getContentText());
      return false;
    }
  } catch (e) {
    Logger.log('  Webhook error: ' + e.message);
    return false;
  }
}

// ==============================================
// TRACKING (PropertiesService)
// ==============================================
function getProcessedSet() {
  var props = PropertiesService.getScriptProperties();
  var raw = props.getProperty(CONFIG.PROCESSED_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (e) {
    return {};
  }
}

function markProcessed(fileId) {
  var processed = getProcessedSet();
  processed[fileId] = new Date().toISOString();

  // Keep only last 500 entries to avoid property size limits (9KB)
  var keys = Object.keys(processed);
  if (keys.length > 500) {
    keys.sort(function(a, b) {
      return processed[a] < processed[b] ? -1 : 1;
    });
    var trimmed = {};
    for (var i = keys.length - 500; i < keys.length; i++) {
      trimmed[keys[i]] = processed[keys[i]];
    }
    processed = trimmed;
  }

  PropertiesService.getScriptProperties().setProperty(
    CONFIG.PROCESSED_KEY,
    JSON.stringify(processed)
  );
}

// ==============================================
// UTILITY
// ==============================================
function getExtension(fileName) {
  var parts = fileName.split('.');
  if (parts.length < 2) return '';
  return parts[parts.length - 1].toLowerCase();
}

// ==============================================
// TRIGGER MANAGEMENT
// ==============================================

/**
 * Run this ONCE to install the 15-minute trigger.
 * Select "installTrigger" from dropdown, click Run.
 */
function installTrigger() {
  // Remove any existing triggers for processInbox
  removeTriggers_();

  ScriptApp.newTrigger('processInbox')
    .timeBased()
    .everyMinutes(15)
    .create();

  Logger.log('Trigger installed: processInbox every 15 minutes');
  Logger.log('Next run will be within 15 minutes.');
}

/**
 * Run this to remove the trigger (pause automation).
 */
function removeTrigger() {
  removeTriggers_();
  Logger.log('All processInbox triggers removed.');
}

function removeTriggers_() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'processInbox') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}
