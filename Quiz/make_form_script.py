"""Generate CreateQuizForm.gs (Google Apps Script) from questions.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""/**
 * Builds the Google Form quiz: one question image (JPEG) + one single-select MCQ per question.
 *
 * Just run createQuizForm() and approve permissions. The edit + student links are printed in the log.
 * If Q01.jpg ... Q__COUNT__.jpg are already in your Drive they are used; otherwise the script draws
 * the question images itself (via a temporary Google Slides deck) and saves them as JPEGs in a
 * Drive folder named "Quiz Question Images".
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

/** Returns one JPEG blob per question: existing Drive images if all are present, else freshly drawn ones. */
function getQuestionImages_() {
  const source = CONFIG.DRIVE_FOLDER_ID ? DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID) : DriveApp;
  const found = QUESTIONS.map(function (_, i) {
    const files = source.getFilesByName(imageName_(i + 1));
    return files.hasNext() ? files.next().getBlob() : null;
  });
  if (found.every(function (b) { return b; })) return found;
  if (CONFIG.DRIVE_FOLDER_ID) throw new Error('Some Q__.jpg images are missing from the Drive folder.');
  return drawQuestionImages_();
}

/** Draws each question on a Slides page, exports it as JPEG and saves it to Drive. */
function drawQuestionImages_() {
  const deck = SlidesApp.create('Quiz question images (temporary)');
  const blank = deck.getSlides()[0];
  QUESTIONS.forEach(function (q, i) {
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

  const folders = DriveApp.getFoldersByName(CONFIG.IMAGE_FOLDER_NAME);
  const folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(CONFIG.IMAGE_FOLDER_NAME);
  const token = ScriptApp.getOAuthToken();
  const blobs = SlidesApp.openById(deck.getId()).getSlides().map(function (slide, i) {
    const url = 'https://docs.google.com/presentation/d/' + deck.getId() +
        '/export/png?pageid=' + slide.getObjectId();
    const png = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token } }).getBlob();
    const jpg = png.getAs('image/jpeg').setName(imageName_(i + 1));
    folder.createFile(jpg);
    return jpg;
  });
  DriveApp.getFileById(deck.getId()).setTrashed(true);
  return blobs;
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
