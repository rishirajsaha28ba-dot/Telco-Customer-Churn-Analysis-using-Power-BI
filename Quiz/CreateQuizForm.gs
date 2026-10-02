/**
 * Builds the Google Form quiz: one question image (JPEG) + one single-select MCQ per question.
 *
 * 1. Upload the images (Q01.jpg ... Q44.jpg) anywhere in your Google Drive.
 * 2. Go to https://script.google.com -> New project, paste this file (CONFIG below is optional).
 * 3. Run createQuizForm() and approve permissions. The edit + live links are printed in the log.
 */
const CONFIG = {
  DRIVE_FOLDER_ID: '',             // optional: leave empty to find Q01.jpg ... anywhere in your Drive
  TITLE: 'Excel, Power BI & SQL Quiz',
  TIME_LIMIT_MINUTES: 30,          // shown to students; enforced by the Form Timer add-on (see README)
  CLOSE_AT: '',                    // optional hard deadline, e.g. '2026-10-05T11:30:00' (script time zone).
                                   // WARNING: closing discards answers of anyone still mid-form; set it a few
                                   // minutes AFTER the timer's auto-submit so partial answers are saved first.
  POINTS_PER_QUESTION: 1,
};

const QUESTIONS = [
  {"options": ["=SUMIF()", "=COUNT()", "=LOOKUP()", "=IF()"], "answer": 3},
  {"options": ["=IF(condition, value_if_true, value_if_false)", "=IF(value_if_true, value_if_false, condition)", "=IF(condition, result)", "=IF(TRUE, FALSE, condition)"], "answer": 0},
  {"options": ["Excel displays an error", "Excel returns the word \"FALSE\"", "Excel leaves the cell blank", "Excel deletes the formula"], "answer": 1},
  {"options": ["OR", "NOT", "XOR", "AND"], "answer": 3},
  {"options": ["To add multiple ranges", "To check multiple conditions in one cell", "To hide error messages", "To format cell colors"], "answer": 1},
  {"options": ["SUMIFS", "IFERROR", "AND", "IFS"], "answer": 3},
  {"options": ["1", "2", "3", "4"], "answer": 2},
  {"options": ["#", "@", "$", "&"], "answer": 2},
  {"options": ["Highlight Cells Rules", "Top/Bottom Rules", "Data Bars", "Icon Sets"], "answer": 1},
  {"options": ["SUM", "SUMIF", "SUMIFS", "COUNTIFS"], "answer": 2},
  {"options": ["AVERAGE", "AVERAGEIF", "AVERAGEIFS", "SUMIFS"], "answer": 2},
  {"options": ["Pivot Table", "Data Validation", "Text to Columns", "Freeze Panes"], "answer": 0},
  {"options": ["CLEAN", "TRIM", "ROUND", "VALUE"], "answer": 1},
  {"options": ["Filter", "Merge Cells", "Freeze Panes", "Format Painter"], "answer": 0},
  {"options": ["15.67", "15.68", "15.70", "16.00"], "answer": 1},
  {"options": ["Enter >AVERAGE(Sales) directly under the Sales heading", "Use a formula-based criteria in a separate criteria column", "Use Sort Largest to Smallest", "Use Data Validation"], "answer": 1},
  {"options": ["Remove Duplicates", "Advanced Filter → Copy to another location → Unique records only", "Sort A to Z", "Conditional Formatting"], "answer": 1},
  {"options": ["*LAP", "LAP*", "?LAP", "*LAP*"], "answer": 1},
  {"options": ["Blank cells become the highest values", "Blank values are generally placed toward the bottom when sorting descending", "Rows containing blanks are automatically deleted", "Excel fills blanks with zero"], "answer": 1},
  {"options": ["Split", "Freeze Panes", "Page Break", "View Side by Side"], "answer": 1},
  {"options": ["=LEFT(A2,3)", "=RIGHT(A2,3)", "=MID(A2,3)", "=LEN(A2,3)"], "answer": 0},
  {"options": ["=CONCAT(A2,B2)", "=CONCAT(A2,\" \",B2)", "=COMBINE(A2,B2)", "=JOIN(A2+B2)"], "answer": 1},
  {"options": ["SUM", "SUBTOTAL", "COUNTIF", "SUMPRODUCT"], "answer": 1},
  {"options": ["Different font sizes", "Extra spaces or inconsistent text formatting", "Different column widths", "Hidden gridlines"], "answer": 1},
  {"options": ["LARGE", "MAX", "RANK.EQ", "HIGH"], "answer": 0},
  {"options": ["COUNT(A:A)", "COUNTA(A:A)", "COUNTA(UNIQUE(A2:A10001))", "SUM(A:A)"], "answer": 2},
  {"options": ["Pie/Donut chart", "Line chart", "Scatter plot", "Histogram only"], "answer": 0},
  {"options": ["Column number", "Row number", "Table number", "Match type"], "answer": 1},
  {"options": ["The first criteria range", "The criteria", "The sum range", "The sheet name"], "answer": 2},
  {"options": ["Different cell colors", "Hidden columns", "Trailing/leading spaces or inconsistent formatting", "Different font sizes"], "answer": 2},
  {"options": ["Pie chart", "Line chart", "Donut chart", "Scatter plot"], "answer": 1},
  {"options": ["A strong positive relationship", "A weak relationship", "A strong negative relationship", "No relationship"], "answer": 2},
  {"options": ["Interquartile Range (IQR)", "VLOOKUP", "SUMIFS", "Data Validation"], "answer": 0},
  {"options": ["=ERROR()", "=ISERROR()", "=IFERROR()", "=CHECKERR()"], "answer": 2},
  {"options": ["To create charts automatically", "To import, clean, and transform data before loading it into a worksheet", "To protect a workbook with a password", "To record keyboard shortcuts"], "answer": 1},
  {"options": ["=INDEX(A2:A10,MATCH(F2,D2:D10,0))", "=INDEX(D2:D10,MATCH(F2,A2:A10,0))", "=MATCH(D2:D10,F2,0)", "=XLOOKUP(D2:D10,F2,A2:A10)"], "answer": 1},
  {"options": ["=SUM(UNIQUE())", "=SORT(UNIQUE(A2:A100))", "=FILTER(SUM(A2:A100))", "=MATCH(SORT(A2:A100))"], "answer": 1},
  {"options": ["Text Box", "Shape", "Slicer connected to the underlying PivotTable", "Page Break"], "answer": 2},
  {"options": ["Write and compile C++ programs", "Connect to, transform, model, and visualize data for business intelligence", "Manage email servers", "Design mobile app UIs only"], "answer": 1},
  {"options": ["COUNT()", "LENGTH_OF()", "TOTALX()", "GROUPX()"], "answer": 0},
  {"options": ["DELETE TABLE", "REMOVE TABLE", "DROP TABLE", "TRUNCATE COLUMN"], "answer": 2},
  {"options": ["Sorts results alphabetically", "Removes duplicate rows from the result set", "Locks a table for editing", "Creates an index on a column"], "answer": 1},
  {"options": ["To sort results", "To filter rows based on a specified condition", "To create a new table", "To group rows together"], "answer": 1},
  {"options": ["NEW TABLE Customers (CustomerID INT)", "CREATE TABLE Customers (CustomerID INT)", "MAKE TABLE Customers (CustomerID INT)", "TABLE CREATE Customers (CustomerID INT)"], "answer": 1}
];

function createQuizForm() {
  const source = CONFIG.DRIVE_FOLDER_ID ? DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID) : DriveApp;
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
    const files = source.getFilesByName(name);
    if (!files.hasNext()) throw new Error('Image not found in Drive: ' + name);

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
