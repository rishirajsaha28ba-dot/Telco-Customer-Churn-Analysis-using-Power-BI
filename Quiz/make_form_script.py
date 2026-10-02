"""Generate CreateQuizForm.gs (Google Apps Script) from questions.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""/**
 * Builds a Google Form quiz: for every question, a JPEG of the question text followed by a
 * single-select multiple-choice item (graded, 1 point each).
 *
 * HOW TO USE: run createQuizForm() once and approve the permissions. That's it.
 *  - Question images are drawn automatically and saved as JPEGs in the Drive folder "Quiz Question Images".
 *  - If Google's 6-minute limit is near, the script schedules itself to continue a minute later.
 *  - When the form is ready, its edit and student links are emailed to you (and written to the log).
 *  - Running it again never creates a duplicate form (unless the questions changed);
 *    run resetQuiz() first if you want a fresh one anyway.
 */
const CONFIG = {
  TITLE: 'Excel, Power BI & SQL Quiz',
  TIME_LIMIT_MINUTES: 30,          // shown to students; enforced by the Form Timer add-on
  CLOSE_AT: '',                    // optional hard deadline, e.g. '2026-10-05T11:30:00' (script time zone).
                                   // Closing discards answers of anyone still mid-form, so set it a few
                                   // minutes AFTER the timer's auto-submit.
  POINTS_PER_QUESTION: 1,
  IMAGE_FOLDER_NAME: 'Quiz Question Images',
};

const QUESTIONS = __QUESTIONS__;

const PROPS = PropertiesService.getScriptProperties();
const RUN_BUDGET_MS = 4.5 * 60 * 1000;   // leave headroom under Google's 6-minute limit
const START = Date.now();

function createQuizForm() {
  clearContinuation_();

  const existingId = PROPS.getProperty('FORM_ID');
  if (existingId && PROPS.getProperty('FORM_QUESTIONS') === questionsSignature_()) {
    const form = FormApp.openById(existingId);
    Logger.log('The quiz form already exists (run resetQuiz() to build a new one).');
    logLinks_(form);
    return;
  }

  const images = getQuestionImages_();
  if (!images) {
    scheduleContinuation_();
    return;
  }
  const form = buildForm_(images);
  PROPS.setProperties({ FORM_ID: form.getId(), FORM_QUESTIONS: questionsSignature_() });
  if (CONFIG.CLOSE_AT) scheduleClose_(new Date(CONFIG.CLOSE_AT));
  logLinks_(form);
  emailLinks_(form);
}

/** Changes whenever the question list changes, so an edited quiz gets a new form. */
function questionsSignature_() {
  return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, JSON.stringify(QUESTIONS)));
}

/** Forgets the previously built form (the form itself is kept in Drive) so the next run builds a new one. */
function resetQuiz() {
  PROPS.deleteProperty('FORM_ID');
  clearContinuation_();
  Logger.log('Reset done. Run createQuizForm() to build a new form.');
}

function buildForm_(images) {
  const form = FormApp.create(CONFIG.TITLE);
  form.setDescription(
      'Time limit: ' + CONFIG.TIME_LIMIT_MINUTES + ' minutes. The form auto-submits when time runs out, ' +
      'and the answers you have marked so far are recorded.\n' +
      'Each question has exactly one correct answer.')
    .setIsQuiz(true)
    .setCollectEmail(true)
    .setLimitOneResponsePerUser(true)
    .setShowLinkToRespondAgain(false)
    .setProgressBar(true)
    .setPublishingSummary(false)
    .setAllowResponseEdits(false)
    .setShuffleQuestions(false);

  QUESTIONS.forEach(function (q, i) {
    form.addImageItem()
      .setTitle('Question ' + (i + 1))
      .setImage(images[i])
      .setAlignment(FormApp.Alignment.CENTER)
      .setWidth(740);

    const item = form.addMultipleChoiceItem();      // single-select (radio buttons)
    item.setTitle('Answer')
      .setChoices(q.options.map(function (opt, j) { return item.createChoice(opt, j === q.answer); }))
      .setPoints(CONFIG.POINTS_PER_QUESTION)
      .setRequired(false);                          // never block a timed auto-submit
  });
  return form;
}

// ---------- Question images ----------

function imageName_(n) {
  return 'Q' + (n < 10 ? '0' + n : n) + '.jpg';
}

function imageFolder_() {
  const folders = DriveApp.getFoldersByName(CONFIG.IMAGE_FOLDER_NAME);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(CONFIG.IMAGE_FOLDER_NAME);
}

/** Returns one JPEG blob per question, or null if time ran out before all images were drawn. */
function getQuestionImages_() {
  const folder = imageFolder_();
  const find = function (i) {
    const files = folder.getFilesByName(imageName_(i + 1));
    return files.hasNext() ? files.next().getBlob() : null;
  };
  let blobs = QUESTIONS.map(function (_, i) { return find(i); });
  const missing = [];
  blobs.forEach(function (b, i) { if (!b) missing.push(i); });
  if (!missing.length) return blobs;

  Logger.log('Drawing ' + missing.length + ' question images...');
  drawQuestionImages_(missing, folder);
  blobs = QUESTIONS.map(function (_, i) { return blobs[i] || find(i); });
  return blobs.every(Boolean) ? blobs : null;
}

/** Draws questions on a temporary Slides deck and saves each page as a JPEG, until time runs low. */
function drawQuestionImages_(indexes, folder) {
  const DECK_NAME = 'Quiz question images (temporary)';
  const old = DriveApp.getFilesByName(DECK_NAME);   // leftovers from an interrupted run
  while (old.hasNext()) old.next().setTrashed(true);

  const deck = SlidesApp.create(DECK_NAME);
  try {
    const blank = deck.getSlides()[0];
    const slides = indexes.map(function (i) { return drawSlide_(deck, i); });
    blank.remove();
    deck.saveAndClose();

    const token = ScriptApp.getOAuthToken();
    for (let k = 0; k < slides.length; k++) {
      if (Date.now() - START > RUN_BUDGET_MS) {
        Logger.log('Time is nearly up; ' + (slides.length - k) + ' images left for the next run.');
        return;
      }
      const url = 'https://docs.google.com/presentation/d/' + deck.getId() + '/export/png?pageid=' + slides[k];
      folder.createFile(fetchWithRetry_(url, token).getAs('image/jpeg').setName(imageName_(indexes[k] + 1)));
      Utilities.sleep(2000);                        // stay under Google's export rate limit
    }
  } finally {
    DriveApp.getFileById(deck.getId()).setTrashed(true);
  }
}

/** Adds one slide for question i and returns its page id. */
function drawSlide_(deck, i) {
  const q = QUESTIONS[i];
  const slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  slide.getBackground().setSolidFill('#FFFFFF');
  slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, 8, 405).getFill().setSolidFill('#1A7F37');

  slide.insertTextBox('Question ' + (i + 1), 40, 24, 640, 44).getText().getTextStyle()
    .setFontFamily('Roboto').setFontSize(26).setBold(true).setForegroundColor('#1A7F37');

  const size = q.q.length <= 120 ? 22 : q.q.length <= 220 ? 19 : 17;
  const body = slide.insertTextBox(q.q, 40, 80, 640, 300).getText();
  body.getTextStyle().setFontFamily('Roboto').setFontSize(size).setForegroundColor('#1F2328');
  body.getParagraphs().forEach(function (p) {     // indented lines are data/formulas: monospace
    const r = p.getRange();
    if (/^ {4}/.test(r.asString())) r.getTextStyle().setFontFamily('Roboto Mono').setBold(true);
  });
  return slide.getObjectId();
}

/** Fetches a URL, backing off and retrying on 429 (too many requests) or 5xx errors. */
function fetchWithRetry_(url, token) {
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token }, muteHttpExceptions: true });
    const code = res.getResponseCode();
    if (code === 200) return res.getBlob();
    if (code !== 429 && code < 500) throw new Error('Image export failed with HTTP ' + code);
    Utilities.sleep(5000 * Math.pow(2, attempt));   // 5s, 10s, 20s, 40s, 80s
  }
  throw new Error('Google is still rate-limiting image export. Wait a few minutes and run again; ' +
      'images already saved are reused.');
}

// ---------- Triggers, links ----------

function scheduleContinuation_() {
  ScriptApp.newTrigger('createQuizForm').timeBased().after(60 * 1000).create();
  Logger.log('Continuing automatically in about a minute. The links will be emailed to you when the form is ready.');
}

function clearContinuation_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'createQuizForm') ScriptApp.deleteTrigger(t);
  });
}

/** Stops accepting responses at a fixed time (in addition to the per-student timer). */
function scheduleClose_(when) {
  ScriptApp.newTrigger('closeForm').timeBased().at(when).create();
  Logger.log('Form will close at ' + when);
}

function closeForm() {
  FormApp.openById(PROPS.getProperty('FORM_ID')).setAcceptingResponses(false)
    .setCustomClosedFormMessage('Time is up. This quiz is now closed.');
}

function logLinks_(form) {
  Logger.log('Edit link:    ' + form.getEditUrl());
  Logger.log('Student link: ' + form.getPublishedUrl());
}

function emailLinks_(form) {
  MailApp.sendEmail(Session.getEffectiveUser().getEmail(), 'Your quiz form is ready: ' + CONFIG.TITLE,
      'Edit link:    ' + form.getEditUrl() + '\n' +
      'Student link: ' + form.getPublishedUrl() + '\n\n' +
      'Next: open the edit link, add the Form Timer add-on (Add-ons menu), set the time limit and turn on auto-submit.');
}
"""

if __name__ == "__main__":
    with open(os.path.join(HERE, "questions.json"), encoding="utf-8") as f:
        qs = json.load(f)
    body = "[\n" + ",\n".join("  " + json.dumps(q, ensure_ascii=False) for q in qs) + "\n]"
    code = TEMPLATE.replace("__QUESTIONS__", body).replace("__COUNT__", f"{len(qs):02d}")
    with open(os.path.join(HERE, "CreateQuizForm.gs"), "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Wrote CreateQuizForm.gs with {len(qs)} questions")
