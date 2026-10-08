/**
 * ELSC Game - score server.
 *
 * A Google Apps Script "web app" attached to a Google Sheet. It keeps the shared high scores
 * and counts how many people play. Setup steps: server/SETUP_SCORES.md
 *
 * The game talks to it with simple web requests:
 *   GET  ?action=top&level=1&edition=site  -> the top 10 for that level and edition
 *   GET  ?action=stats              -> total plays, plays today, best score per level
 *   POST {"action":"start", ...}    -> a run started   (counts a play)
 *   POST {"action":"finish", ...}   -> a run ended     (how far they got)
 *   POST {"action":"score", ...}    -> save a high score
 * POST bodies are JSON sent as plain text (no special headers), so browsers allow it.
 *
 * Editions: the same game is published twice, "site" (on the website) and "friends" (the link you give
 * to friends). Every play and score is tagged with its edition, and each edition has its own top 10.
 */

// ---------------------------------------------------------------- settings
var TOP_N = 10;
var MAX_NAME = 10;
// The highest score the game allows: 150 bar points x 10 + 1000 for passing, per stage, x the level.
// IMPORTANT: if you change the score numbers in the game's settings.py (SCORE_PER_POINT, the pass bonus,
// the multipliers, the bar size or the number of stages), update MAX_SCORE too, or real scores get refused.
var MAX_SCORE = { 1: 7500, 2: 25000, 3: 37500 };
var MIN_RUN_SECONDS = 25;          // a score must come at least this long after its "start"
var SESSION_HOURS = 6;             // how long a play session stays valid for sending its score
// Names that contain these are saved as PLAYER (add your own, uppercase).
var BAD_PARTS = ['FUCK', 'SHIT', 'BITCH', 'PUSSY', 'CUNT', 'PORN', 'NIGGER', 'NIGGA', 'FAGGOT',
                 'HITLER', 'NAZI', 'WHORE', 'SLUT', 'UNKO', 'CHINKO', 'CHINPO', 'MANKO', 'KUSO'];
// Short words that are only blocked when they are the whole name or a whole word.
// (DICK and RAPE are here, not above, so names like DICKSON, BENEDICK, GRAPE or DRAPER are kept.)
var BAD_WORDS = ['ASS', 'SEX', 'FAG', 'DIE', 'KILL', 'BAKA', 'TITS', 'DICK', 'RAPE'];
var EDITIONS = ['site', 'friends'];

// ---------------------------------------------------------------- run once from the editor
function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  sheet_(ss, 'Plays', ['Time', 'Session', 'Event', 'Level', 'Character', 'Stage reached', 'Score', 'Finished level', 'Edition', 'Device']);
  sheet_(ss, 'Scores', ['Time', 'Level', 'Name', 'Score', 'Session', 'Edition']);
  var sum = sheet_(ss, 'Summary', ['What', 'Number']);
  var rows = [
    ['Games started (all time)', '=COUNTIF(Plays!C:C,"start")'],
    ['Games started today', '=COUNTIFS(Plays!C:C,"start",Plays!A:A,">="&TODAY())'],
    ['Games started in the last 7 days', '=COUNTIFS(Plays!C:C,"start",Plays!A:A,">="&(TODAY()-6))'],
    ['Games from the website', '=COUNTIFS(Plays!C:C,"start",Plays!I:I,"site")'],
    ['Games from the friends link', '=COUNTIFS(Plays!C:C,"start",Plays!I:I,"friends")'],
    ['Games on phones / tablets', '=COUNTIFS(Plays!C:C,"start",Plays!J:J,"phone")'],
    ['Games on computers', '=COUNTIFS(Plays!C:C,"start",Plays!J:J,"computer")'],
    ['Level 1 games', '=COUNTIFS(Plays!C:C,"start",Plays!D:D,1)'],
    ['Level 2 games', '=COUNTIFS(Plays!C:C,"start",Plays!D:D,2)'],
    ['Level 3 games', '=COUNTIFS(Plays!C:C,"start",Plays!D:D,3)'],
    ['Played as the boy', '=COUNTIFS(Plays!C:C,"start",Plays!E:E,"boy")'],
    ['Played as the girl', '=COUNTIFS(Plays!C:C,"start",Plays!E:E,"girl")'],
    ['Finished Level 1', '=COUNTIFS(Plays!C:C,"finish",Plays!D:D,1,Plays!H:H,TRUE)'],
    ['Finished Level 2', '=COUNTIFS(Plays!C:C,"finish",Plays!D:D,2,Plays!H:H,TRUE)'],
    ['Finished Level 3', '=COUNTIFS(Plays!C:C,"finish",Plays!D:D,3,Plays!H:H,TRUE)'],
    ['Best score Level 1', '=IFERROR(MAXIFS(Scores!D:D,Scores!B:B,1),0)'],
    ['Best score Level 2', '=IFERROR(MAXIFS(Scores!D:D,Scores!B:B,2),0)'],
    ['Best score Level 3', '=IFERROR(MAXIFS(Scores!D:D,Scores!B:B,3),0)'],
    ['High scores saved', '=MAX(0,COUNTA(Scores!A:A)-1)']
  ];
  sum.getRange(2, 1, rows.length, 2).setValues(rows);
  sum.autoResizeColumn(1);
  return 'ELSC score sheet is ready';
}

function sheet_(ss, name, headers) {
  var sh = ss.getSheetByName(name) || ss.insertSheet(name);
  sh.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
  sh.setFrozenRows(1);
  return sh;
}

// ---------------------------------------------------------------- web requests
function doGet(e) {
  var p = (e && e.parameter) || {};
  try {
    if (p.action === 'top') return json_({ ok: true, level: level_(p.level), edition: edition_(p.edition), top: top_(level_(p.level), edition_(p.edition)) });
    if (p.action === 'stats') return json_(stats_(edition_(p.edition)));
    return json_({ ok: true, game: 'ELSC Game score server' });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doPost(e) {
  var body;
  try {
    body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
  } catch (err) {
    return json_({ ok: false, error: 'bad json' });
  }
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(8000);
  } catch (err) {
    return json_({ ok: false, error: 'busy, try again' });
  }
  try {
    if (body.action === 'start') return json_(start_(body));
    if (body.action === 'finish') return json_(finish_(body));
    if (body.action === 'score') return json_(score_(body));
    return json_({ ok: false, error: 'unknown action' });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------- actions
function start_(b) {
  var session = session_(b.session);
  var level = level_(b.level);
  var who = b.character === 'girl' ? 'girl' : 'boy';
  CacheService.getScriptCache().put('start_' + session, String(Date.now()), SESSION_HOURS * 3600);
  book_().getSheetByName('Plays').appendRow([new Date(), session, 'start', level, who, '', '', '', edition_(b.edition), device_(b.device)]);
  return { ok: true };
}

function finish_(b) {
  var session = session_(b.session);
  var level = level_(b.level);
  var who = b.character === 'girl' ? 'girl' : 'boy';
  var stage = Math.max(1, Math.min(5, parseInt(b.stage, 10) || 1));
  var score = clampScore_(b.score, level);
  book_().getSheetByName('Plays').appendRow([new Date(), session, 'finish', level, who, stage, score, b.completed === true, edition_(b.edition), device_(b.device)]);
  return { ok: true };
}

function score_(b) {
  var session = session_(b.session);
  var level = level_(b.level);
  var score = parseInt(b.score, 10);
  if (!(score >= 0) || score > MAX_SCORE[level]) return { ok: false, error: 'score out of range' };
  var cache = CacheService.getScriptCache();
  var started = parseInt(cache.get('start_' + session), 10);
  if (!started) return { ok: false, error: 'unknown session' };
  if ((Date.now() - started) / 1000 < MIN_RUN_SECONDS) return { ok: false, error: 'too fast' };
  if (cache.get('scored_' + session)) return { ok: false, error: 'already saved' };
  var name = cleanName_(b.name);
  var edition = edition_(b.edition);
  book_().getSheetByName('Scores').appendRow([new Date(), level, name, score, session, edition]);
  cache.put('scored_' + session, '1', SESSION_HOURS * 3600);
  cache.remove('top_' + edition + '_' + level);
  cache.remove('stats_' + edition);
  var top = top_(level, edition);
  var rank = 0;
  for (var i = 0; i < top.length; i++) {
    if (top[i].name === name && top[i].score === score) { rank = i + 1; break; }
  }
  return { ok: true, name: name, rank: rank, top: top };
}

// ---------------------------------------------------------------- reading
function top_(level, edition) {
  var cache = CacheService.getScriptCache();
  var hit = cache.get('top_' + edition + '_' + level);
  if (hit) return JSON.parse(hit);
  var sh = book_().getSheetByName('Scores');
  var last = sh.getLastRow();
  var list = [];
  if (last >= 2) {
    var rows = sh.getRange(2, 1, last - 1, 6).getValues();     // Time, Level, Name, Score, Session, Edition
    for (var i = 0; i < rows.length; i++) {
      if (Number(rows[i][1]) === level && edition_(rows[i][5]) === edition) {
        list.push({ name: String(rows[i][2]), score: Number(rows[i][3]), t: new Date(rows[i][0]).getTime() });
      }
    }
  }
  // highest first; on a tie, whoever got it first stays above
  list.sort(function (a, b) { return b.score - a.score || a.t - b.t; });
  list = list.slice(0, TOP_N).map(function (r) { return { name: r.name, score: r.score }; });
  cache.put('top_' + edition + '_' + level, JSON.stringify(list), 30);
  return list;
}

function stats_(edition) {
  var cache = CacheService.getScriptCache();
  var hit = cache.get('stats_' + edition);
  if (hit) return JSON.parse(hit);
  var sh = book_().getSheetByName('Plays');
  var last = sh.getLastRow();
  var total = 0, today = 0;
  var midnight = new Date();
  midnight.setHours(0, 0, 0, 0);
  if (last >= 2) {
    var rows = sh.getRange(2, 1, last - 1, 9).getValues();     // Time, Session, Event, ..., Edition
    for (var i = 0; i < rows.length; i++) {
      if (rows[i][2] === 'start' && edition_(rows[i][8]) === edition) {
        total++;
        if (new Date(rows[i][0]) >= midnight) today++;
      }
    }
  }
  var best = {};
  [1, 2, 3].forEach(function (lv) {
    var t = top_(lv, edition);
    best[lv] = t.length ? t[0] : null;
  });
  var out = { ok: true, edition: edition, plays: total, plays_today: today, best: best };
  cache.put('stats_' + edition, JSON.stringify(out), 60);
  return out;
}

// ---------------------------------------------------------------- helpers
function book_() {
  return SpreadsheetApp.getActiveSpreadsheet();
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function level_(v) {
  var n = parseInt(v, 10);
  return n === 2 || n === 3 ? n : 1;
}

function edition_(v) {
  return EDITIONS.indexOf(String(v)) !== -1 ? String(v) : 'site';
}

function device_(v) {
  return v === 'phone' ? 'phone' : 'computer';
}

function session_(v) {
  var s = String(v || '').replace(/[^A-Za-z0-9]/g, '').slice(0, 32);
  if (s.length < 8) throw new Error('bad session');
  return s;
}

function clampScore_(v, level) {
  var n = parseInt(v, 10);
  if (!(n >= 0)) return 0;
  return Math.min(n, MAX_SCORE[level]);
}

function cleanName_(v) {
  var name = String(v || '').toUpperCase().replace(/[^A-Z0-9 ]/g, '').replace(/\s+/g, ' ').trim().slice(0, MAX_NAME);
  if (!name) return 'PLAYER';
  var squashed = name.replace(/ /g, '');
  for (var i = 0; i < BAD_PARTS.length; i++) {
    if (squashed.indexOf(BAD_PARTS[i]) !== -1) return 'PLAYER';
  }
  var words = name.split(' ');
  for (var j = 0; j < words.length; j++) {
    if (BAD_WORDS.indexOf(words[j]) !== -1) return 'PLAYER';
  }
  if (BAD_WORDS.indexOf(squashed) !== -1) return 'PLAYER';
  return name;
}

// ---------------------------------------------------------------- quick self-test (run from the editor)
function testNames() {
  var cases = ['mike', 'Haruna!!', '  a  b  ', 'classPASS', 'kill', 'BIGASS', 'f u c k', ''];
  return cases.map(function (c) { return c + ' -> ' + cleanName_(c); }).join('\n');
}
