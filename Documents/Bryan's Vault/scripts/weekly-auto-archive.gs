/**
 * Weekly Auto-Archive
 * Google Drive Organization Project - Recurring Automation
 *
 * Runs every Sunday at 3 AM ET. Scans numbered top-level folders for files
 * older than STALE_DAYS (default 90). Moves stale files to 90_ARCHIVE
 * in a dated subfolder (e.g., 90_ARCHIVE/archived_2026-03).
 *
 * Skips: 00_INBOX (handled by CV Auto-Sort), 90_ARCHIVE, 91_SYSTEM.
 * Only archives files, never folders.
 *
 * DEPLOYMENT:
 * 1. Go to https://script.google.com
 * 2. Click "+ New project", name it "Weekly Auto-Archive"
 * 3. Delete default code, paste ALL of this
 * 4. Save (Ctrl+S)
 * 5. Select "installTrigger" from the function dropdown, click Run
 *    - First run: click "Review permissions" > choose your Google account > Allow
 * 6. Verify trigger appears in Triggers tab (clock icon, left sidebar)
 *
 * To run manually: select "runWeeklyArchive" and click Run
 * To do a dry run first: select "dryRun" and click Run (logs only, no moves)
 * To stop: delete the trigger from the Triggers tab
 */

// ==============================================
// CONFIGURATION
// ==============================================
var ARCHIVE_CONFIG = {
  // Files older than this many days get archived
  STALE_DAYS: 90,

  // Archive destination
  ARCHIVE_FOLDER_ID: '1VI29XLZ2_BzFb-DOghHXfq_gTZlU9Y8K',  // 90_ARCHIVE

  // Folders to scan (top-level only, not recursive)
  SCAN_FOLDERS: [
    { id: '19p0p8_aZKRRhHjvjZSJXxIIzuOcFfOTk', name: '01_CANDIDATES' },
    { id: '1EfzsLK99WVxHctl3p2hM7oKBM09uIRQ4', name: '02_CLIENTS' },
    { id: '1TWF1fERZSYXKW7eSpAWKOhjrDaIGLb-T', name: '03_SEARCHES' },
    { id: '18UKz22GoyYA70eioIFn-cmeGjsz6hU0L', name: '04_CONTENT' },
    { id: '1RayGJHgs3iCdNoDp-0b1d5gaSaXg0kUF', name: '05_FRAMEWORKS' },
    { id: '114s9TZRCNc73-ucF9EhHSIgjyek20wMx', name: '06_BUSINESS_OPS' },
    { id: '1w5fZPjmQ38ZRN7C8zgY0fkW3K8YHaAs1', name: '10_LEARNING' },
    { id: '1TruitczH5YI5pQobyjsfbsGEAJtVMvp1', name: '30_PERSONAL' }
  ],

  // Max files per run to avoid 6-minute timeout
  BATCH_SIZE: 50,

  // Max runtime in ms (5 min safety margin)
  MAX_RUN_MS: 5 * 60 * 1000
};

// ==============================================
// MAIN FUNCTION
// ==============================================
function runWeeklyArchive() {
  runArchive_(false);
}

function dryRun() {
  runArchive_(true);
}

function runArchive_(isDryRun) {
  var mode = isDryRun ? 'DRY RUN' : 'LIVE';
  Logger.log('=== Weekly Auto-Archive: STARTING (' + mode + ') ===');
  Logger.log('Timestamp: ' + new Date().toISOString());
  Logger.log('Stale threshold: ' + ARCHIVE_CONFIG.STALE_DAYS + ' days');

  var startTime = new Date().getTime();
  var cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - ARCHIVE_CONFIG.STALE_DAYS);
  Logger.log('Cutoff date: ' + cutoffDate.toISOString());

  // Get or create monthly archive subfolder (e.g., "archived_2026-03")
  var monthTag = Utilities.formatDate(new Date(), 'America/New_York', 'yyyy-MM');
  var archiveSubfolder = isDryRun ? null : getOrCreateSubfolder_(
    ARCHIVE_CONFIG.ARCHIVE_FOLDER_ID,
    'archived_' + monthTag
  );

  var totalMoved = 0;
  var totalSkipped = 0;
  var errors = [];

  for (var f = 0; f < ARCHIVE_CONFIG.SCAN_FOLDERS.length; f++) {
    // Check runtime
    if (new Date().getTime() - startTime > ARCHIVE_CONFIG.MAX_RUN_MS) {
      Logger.log('TIMEOUT: hit ' + (ARCHIVE_CONFIG.MAX_RUN_MS / 60000) + ' min limit. Will continue next run.');
      break;
    }

    if (totalMoved >= ARCHIVE_CONFIG.BATCH_SIZE) {
      Logger.log('BATCH LIMIT: reached ' + ARCHIVE_CONFIG.BATCH_SIZE + ' files. Will continue next run.');
      break;
    }

    var folderDef = ARCHIVE_CONFIG.SCAN_FOLDERS[f];
    Logger.log('\nScanning: ' + folderDef.name);

    try {
      var folder = DriveApp.getFolderById(folderDef.id);
      var files = folder.getFiles();
      var folderMoved = 0;
      var folderSkipped = 0;

      while (files.hasNext() && totalMoved < ARCHIVE_CONFIG.BATCH_SIZE) {
        var file = files.next();
        var lastUpdated = file.getLastUpdated();

        if (lastUpdated < cutoffDate) {
          if (isDryRun) {
            Logger.log('  WOULD ARCHIVE: ' + file.getName() +
              ' (last updated: ' + lastUpdated.toISOString().substring(0, 10) + ')');
          } else {
            try {
              file.moveTo(archiveSubfolder);
              Logger.log('  ARCHIVED: ' + file.getName() +
                ' (last updated: ' + lastUpdated.toISOString().substring(0, 10) + ')');
            } catch (e) {
              errors.push(file.getName() + ': ' + e.message);
              Logger.log('  ERROR moving ' + file.getName() + ': ' + e.message);
              continue;
            }
          }
          folderMoved++;
          totalMoved++;
        } else {
          folderSkipped++;
          totalSkipped++;
        }
      }

      Logger.log('  ' + folderDef.name + ': ' + folderMoved + ' archived, ' + folderSkipped + ' current');

    } catch (e) {
      errors.push(folderDef.name + ': ' + e.message);
      Logger.log('  ERROR accessing ' + folderDef.name + ': ' + e.message);
    }
  }

  // Summary
  Logger.log('\n--- Summary ---');
  Logger.log('Mode: ' + mode);
  Logger.log('Files archived: ' + totalMoved);
  Logger.log('Files current (kept): ' + totalSkipped);
  Logger.log('Errors: ' + errors.length);
  if (errors.length > 0) {
    Logger.log('Error details: ' + errors.join('; '));
  }
  Logger.log('Runtime: ' + ((new Date().getTime() - startTime) / 1000).toFixed(1) + 's');
  Logger.log('=== Weekly Auto-Archive: DONE ===');
}

// ==============================================
// UTILITY
// ==============================================
function getOrCreateSubfolder_(parentId, name) {
  var parent = DriveApp.getFolderById(parentId);
  var existing = parent.getFoldersByName(name);
  if (existing.hasNext()) {
    return existing.next();
  }
  return parent.createFolder(name);
}

// ==============================================
// TRIGGER MANAGEMENT
// ==============================================

/**
 * Run this ONCE to install the weekly Sunday 3AM trigger.
 * Select "installTrigger" from dropdown, click Run.
 */
function installTrigger() {
  // Remove any existing triggers for runWeeklyArchive
  removeTriggers_();

  ScriptApp.newTrigger('runWeeklyArchive')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY)
    .atHour(3)
    .create();

  Logger.log('Trigger installed: runWeeklyArchive every Sunday 3-4 AM');
  Logger.log('Next run will be this coming Sunday between 3:00 and 4:00 AM.');
}

/**
 * Run this to remove the trigger (pause automation).
 */
function removeTrigger() {
  removeTriggers_();
  Logger.log('All runWeeklyArchive triggers removed.');
}

function removeTriggers_() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'runWeeklyArchive') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}
