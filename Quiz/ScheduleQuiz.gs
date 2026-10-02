/**
 * Opens the quiz form at OPEN_AT and closes it at CLOSE_AT (India time, +05:30).
 * 1. Set the two times below.  2. Run scheduleQuiz() once and click Allow.
 * Run cancelSchedule() to remove the schedule. Run showSchedule() to see what is set.
 */
const FORM_ID = '1ruTBdglr1HJZYT-32WB4PiVW9ThmQiMdyVFcNZU9mHU';
const OPEN_AT  = '2026-10-05T10:00:00+05:30';   // when students can start
const CLOSE_AT = '2026-10-05T10:40:00+05:30';   // when the form stops accepting answers

function scheduleQuiz() {
  const open = new Date(OPEN_AT), close = new Date(CLOSE_AT);
  if (isNaN(open) || isNaN(close)) throw new Error('OPEN_AT / CLOSE_AT are not valid dates.');
  if (close <= open) throw new Error('CLOSE_AT must be after OPEN_AT.');
  if (close <= new Date()) throw new Error('CLOSE_AT is already in the past.');

  cancelSchedule();
  const form = FormApp.openById(FORM_ID);
  if (open > new Date()) {
    form.setAcceptingResponses(false)
      .setCustomClosedFormMessage('This quiz opens at ' + fmt_(open) + '. Please come back then.');
    ScriptApp.newTrigger('openQuiz').timeBased().at(open).create();
  } else {
    form.setAcceptingResponses(true);
  }
  ScriptApp.newTrigger('closeQuiz').timeBased().at(close).create();
  Logger.log('Quiz opens ' + fmt_(open) + ' and closes ' + fmt_(close) + '.');
  Logger.log('Student link: ' + form.getPublishedUrl());
}

function openQuiz() {
  FormApp.openById(FORM_ID).setAcceptingResponses(true);
}

function closeQuiz() {
  FormApp.openById(FORM_ID).setAcceptingResponses(false)
    .setCustomClosedFormMessage('Time is up. This quiz is now closed.');
}

function cancelSchedule() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (['openQuiz', 'closeQuiz'].indexOf(t.getHandlerFunction()) !== -1) ScriptApp.deleteTrigger(t);
  });
}

function showSchedule() {
  const handlers = ScriptApp.getProjectTriggers().map(function (t) { return t.getHandlerFunction(); });
  Logger.log(handlers.length ? 'Scheduled: ' + handlers.join(', ') : 'Nothing scheduled.');
  Logger.log('Accepting responses now: ' + FormApp.openById(FORM_ID).isAcceptingResponses());
}

function fmt_(d) {
  return Utilities.formatDate(d, 'Asia/Kolkata', 'd MMM yyyy, h:mm a') + ' IST';
}
