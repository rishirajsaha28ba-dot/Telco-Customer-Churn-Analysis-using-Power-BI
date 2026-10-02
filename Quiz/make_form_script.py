"""Generate CreateQuizForm.gs (Google Apps Script) from questions.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""/**
 * Builds the Google Form quiz: one question image (JPEG) + one single-select MCQ per question.
 *
 * 1. Upload the images/ folder (Q01.jpg ... Q__COUNT__.jpg) to Google Drive and copy the folder ID
 *    from its URL (drive.google.com/drive/folders/<FOLDER_ID>).
 * 2. Go to https://script.google.com -> New project, paste this file, set CONFIG below.
 * 3. Run createQuizForm() and approve permissions. The edit + live links are printed in the log.
 */
const CONFIG = {
  DRIVE_FOLDER_ID: 'PASTE_FOLDER_ID_HERE',
  TITLE: 'Excel, Power BI & SQL Quiz',
  TIME_LIMIT_MINUTES: 30,          // shown to students; enforced by the Form Timer add-on (see README)
  CLOSE_AT: '',                    // optional hard deadline, e.g. '2026-10-05T11:30:00' (script time zone).
                                   // WARNING: closing discards answers of anyone still mid-form; set it a few
                                   // minutes AFTER the timer's auto-submit so partial answers are saved first.
  POINTS_PER_QUESTION: 1,
};

const QUESTIONS = __QUESTIONS__;

function createQuizForm() {
  const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
  const form = FormApp.create(CONFIG.TITLE);
  form.setDescription(
      'Time limit: ' + CONFIG.TIME_LIMIT_MINUTES + ' minutes. The form will auto-submit when time runs out.\n' +
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
    const name = 'Q' + (n < 10 ? '0' + n : n) + '.jpg';
    const files = folder.getFilesByName(name);
    if (!files.hasNext()) throw new Error('Missing image in Drive folder: ' + name);

    form.addImageItem()
      .setTitle('Question ' + n)
      .setImage(files.next().getBlob())
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
    slim = [{"options": q["options"], "answer": q["answer"]} for q in qs]
    body = "[\n" + ",\n".join("  " + json.dumps(q, ensure_ascii=False) for q in slim) + "\n]"
    out = TEMPLATE.replace("__QUESTIONS__", body).replace("__COUNT__", f"{len(qs):02d}")
    with open(os.path.join(HERE, "CreateQuizForm.gs"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote CreateQuizForm.gs with {len(qs)} questions")
