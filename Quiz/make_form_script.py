"""Generate CreateQuizForm.gs (Google Apps Script) from questions.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""/**
 * Builds the Google Form quiz: one question image (JPEG) + one single-select MCQ per question.
 *
 * Just run createQuizForm() and approve permissions. The edit + student links are printed in the log.
 * The script draws the question images itself (via a temporary Google Slides deck) and saves them as
 * JPEGs in a Drive folder named "Quiz Question Images". If a run stops part-way, just run it again:
 * images already in that folder are reused.
 */
const CONFIG = {
  TITLE: 'Excel, Power BI & SQL Quiz',
  TIME_LIMIT_MINUTES: 30,          // shown to students; enforced by the Form Timer add-on (see README)
  CLOSE_AT: '',                    // optional hard deadline, e.g. '2026-10-05T11:30:00' (script time zone).
                                   // WARNING: closing discards answers of anyone still mid-form; set it a few
                                   // minutes AFTER the timer's auto-submit so partial answers are saved first.
  POINTS_PER_QUESTION: 1,
  DRIVE_FOLDER_ID: '',             // optional: folder holding your own Q01.jpg ... images
  IMAGE_FOLDER_NAME: 'Quiz Question Images',
};

const QUESTIONS = __QUESTIONS__;

function createQuizForm() {
  const images = getQuestionImages_();
  const form = FormApp.create(CONFIG.TITLE);
  form.setDescription(
      'Time limit: ' + CONFIG.TIME_LIMIT_MINUTES + ' minutes. The form will auto-submit when time runs out, ' +
      'and the answers you have marked so far will be recorded.\n' +
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
    const n = i + 1;
    form.addImageItem()
      .setTitle('Question ' + n)
      .setImage(images[i])
      .setAlignment(FormApp.Alignment.CENTER)
      .setWidth(740);

    const item = form.addMultipleChoiceItem();   // single-select (radio buttons)
    item.setTitle('Answer for Question ' + n)
      .setChoices(q.options.map(function (opt, j) { return item.createChoice(opt, j === q.answer); }))
      .setPoints(CONFIG.POINTS_PER_QUESTION)
      .setRequired(false);                       // not required so a timed auto-submit is never blocked
  });

  if (CONFIG.CLOSE_AT) scheduleClose_(form, new Date(CONFIG.CLOSE_AT));

  Logger.log('Edit link:      ' + form.getEditUrl());
  Logger.log('Student link:   ' + form.getPublishedUrl());
}

function imageName_(n) {
  return 'Q' + (n < 10 ? '0' + n : n) + '.jpg';
}

/** Returns one JPEG blob per question, reusing images already saved and drawing only the missing ones. */
function getQuestionImages_() {
  const folder = CONFIG.DRIVE_FOLDER_ID ? DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID) : imageFolder_();
  const blobs = QUESTIONS.map(function (_, i) {
    const files = folder.getFilesByName(imageName_(i + 1));
    return files.hasNext() ? files.next().getBlob() : null;
  });
  const missing = [];
  blobs.forEach(function (b, i) { if (!b) missing.push(i); });
  if (missing.length && CONFIG.DRIVE_FOLDER_ID) throw new Error('Some Q__.jpg images are missing from the Drive folder.');
  if (missing.length) {
    Logger.log('Drawing ' + missing.length + ' question images...');
    drawQuestionImages_(missing, folder).forEach(function (b, k) { blobs[missing[k]] = b; });
  }
  return blobs;
}

function imageFolder_() {
  const folders = DriveApp.getFoldersByName(CONFIG.IMAGE_FOLDER_NAME);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(CONFIG.IMAGE_FOLDER_NAME);
}

/** Draws the given questions on Slides pages, exports each as JPEG and saves it to the folder. */
function drawQuestionImages_(indexes, folder) {
  const DECK_NAME = 'Quiz question images (temporary)';
  const old = DriveApp.getFilesByName(DECK_NAME);           // leftovers from an earlier failed run
  while (old.hasNext()) old.next().setTrashed(true);

  const deck = SlidesApp.create(DECK_NAME);
  try {
    const blank = deck.getSlides()[0];
    indexes.forEach(function (i) {
      const q = QUESTIONS[i];
      const slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
      slide.getBackground().setSolidFill('#FFFFFF');
      slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, 8, 405).getFill().setSolidFill('#1A7F37');

      const head = slide.insertTextBox('Question ' + (i + 1), 40, 24, 640, 44).getText();
      head.getTextStyle().setFontFamily('Roboto').setFontSize(26).setBold(true).setForegroundColor('#1A7F37');

      const size = q.q.length <= 120 ? 22 : q.q.length <= 220 ? 19 : 17;
      const body = slide.insertTextBox(q.q, 40, 80, 640, 300).getText();
      body.getTextStyle().setFontFamily('Roboto').setFontSize(size).setForegroundColor('#1F2328');
      body.getParagraphs().forEach(function (p) {
        const r = p.getRange();
        if (/^ {4}/.test(r.asString())) r.getTextStyle().setFontFamily('Roboto Mono').setBold(true);
      });
    });
    blank.remove();
    deck.saveAndClose();

    const token = ScriptApp.getOAuthToken();
    return SlidesApp.openById(deck.getId()).getSlides().map(function (slide, k) {
      const url = 'https://docs.google.com/presentation/d/' + deck.getId() +
          '/export/png?pageid=' + slide.getObjectId();
      const jpg = fetchWithRetry_(url, token).getAs('image/jpeg').setName(imageName_(indexes[k] + 1));
      folder.createFile(jpg);                               // saved right away, so a rerun resumes here
      Utilities.sleep(2000);                                // stay under Google's export rate limit
      return jpg;
    });
  } finally {
    DriveApp.getFileById(deck.getId()).setTrashed(true);
  }
}

/** Fetches a URL, waiting and retrying when Google answers 429 (too many requests) or a 5xx error. */
function fetchWithRetry_(url, token) {
  for (let attempt = 0; attempt < 6; attempt++) {
    const res = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token }, muteHttpExceptions: true });
    const code = res.getResponseCode();
    if (code === 200) return res.getBlob();
    if (code !== 429 && code < 500) throw new Error('Image export failed with HTTP ' + code);
    Utilities.sleep(5000 * Math.pow(2, attempt));           // 5s, 10s, 20s, 40s, 80s, 160s
  }
  throw new Error('Google kept rate-limiting image export. Wait a few minutes and run again; ' +
      'images already saved are reused.');
}

/** Stops accepting responses at a fixed time (in addition to the per-student timer). */
function scheduleClose_(form, when) {
  PropertiesService.getScriptProperties().setProperty('FORM_ID', form.getId());
  ScriptApp.newTrigger('closeForm').timeBased().at(when).create();
  Logger.log('Form will close at ' + when);
}

function closeForm() {
  const id = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  FormApp.openById(id).setAcceptingResponses(false)
    .setCustomClosedFormMessage('Time is up. This quiz is now closed.');
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
