/**
 * Builds a Google Form quiz: for every question, a JPEG of the question text followed by a
 * single-select multiple-choice item (graded, 1 point each).
 *
 * HOW TO USE: run createQuizForm() once and approve the permissions. That's it.
 *  - Question images are drawn automatically and saved as JPEGs in the Drive folder "Quiz Question Images".
 *  - If Google's 6-minute limit is near, the script schedules itself to continue a minute later.
 *  - When the form is ready, its edit and student links are emailed to you (and written to the log).
 *  - Running it again never creates a duplicate form; run resetQuiz() first if you want a fresh one.
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

const QUESTIONS = [
  {"q": "Which function is used to return text like \"Pass\" or \"Fail\" based on a condition?", "options": ["=SUMIF()", "=COUNT()", "=LOOKUP()", "=IF()"], "answer": 3},
  {"q": "Which of the following is the correct basic syntax for the IF function in Excel?", "options": ["=IF(condition, value_if_true, value_if_false)", "=IF(value_if_true, value_if_false, condition)", "=IF(condition, result)", "=IF(TRUE, FALSE, condition)"], "answer": 0},
  {"q": "What happens if you do not include the value_if_false part in an IF formula and the condition is false?", "options": ["Excel displays an error", "Excel returns the word \"FALSE\"", "Excel leaves the cell blank", "Excel deletes the formula"], "answer": 1},
  {"q": "Which function can be used with IF when all conditions must be true to return \"Pass\"?", "options": ["OR", "NOT", "XOR", "AND"], "answer": 3},
  {"q": "What is the primary purpose of a \"Nested IF\" formula in Excel?", "options": ["To add multiple ranges", "To check multiple conditions in one cell", "To hide error messages", "To format cell colors"], "answer": 1},
  {"q": "Which function is a simpler and more modern alternative to multiple Nested IF formulas?", "options": ["SUMIFS", "IFERROR", "AND", "IFS"], "answer": 3},
  {"q": "If you want to assign 4 different grades (A, B, C, F) using Nested IF, how many IF statements are usually required?", "options": ["1", "2", "3", "4"], "answer": 2},
  {"q": "Which symbol is used to make a column reference fixed in a Conditional Formatting formula?", "options": ["#", "@", "$", "&"], "answer": 2},
  {"q": "Which option allows you to highlight the top 10% or bottom 10% of values in a dataset?", "options": ["Highlight Cells Rules", "Top/Bottom Rules", "Data Bars", "Icon Sets"], "answer": 1},
  {"q": "You have a sales dataset with columns:\n    • City\n    • Category\n    • Revenue\nYou want total revenue for Bengaluru AND Electronics.\n\nWhich function should you use?", "options": ["SUM", "SUMIF", "SUMIFS", "COUNTIFS"], "answer": 2},
  {"q": "You want to calculate the average revenue of Electronics orders made by Returning Customers.\n\nWhich function is most appropriate?", "options": ["AVERAGE", "AVERAGEIF", "AVERAGEIFS", "SUMIFS"], "answer": 2},
  {"q": "You have 20,000 sales records and want to quickly compare Revenue by City and Category.\n\nWhat is the most appropriate Excel feature?", "options": ["Pivot Table", "Data Validation", "Text to Columns", "Freeze Panes"], "answer": 0},
  {"q": "A dataset contains:\n    \" Bengaluru\"\nand\n    \"Bengaluru \"\n\nWhich Excel function is useful for removing unnecessary spaces?", "options": ["CLEAN", "TRIM", "ROUND", "VALUE"], "answer": 1},
  {"q": "You want to view only:\n    Bengaluru + Electronics + Revenue > ₹10,000\n\nWhich Excel feature is most directly useful?", "options": ["Filter", "Merge Cells", "Freeze Panes", "Format Painter"], "answer": 0},
  {"q": "What will:\n    =ROUND(15.678,2)\nreturn?", "options": ["15.67", "15.68", "15.70", "16.00"], "answer": 1},
  {"q": "You have a column called Sales and want to extract only records where sales are greater than the average sales.\n\nWhich approach is most appropriate for an Advanced Filter?", "options": ["Enter >AVERAGE(Sales) directly under the Sales heading", "Use a formula-based criteria in a separate criteria column", "Use Sort Largest to Smallest", "Use Data Validation"], "answer": 1},
  {"q": "A customer database contains 50,000 records. You need to create a separate list containing only unique customer records, without deleting anything from the original database.\n\nWhich option is most appropriate?", "options": ["Remove Duplicates", "Advanced Filter → Copy to another location → Unique records only", "Sort A to Z", "Conditional Formatting"], "answer": 1},
  {"q": "You have product codes such as:\n    LAP-101, LAP-205, MOB-101, TAB-301, LAPTOP-500\nYou want to extract codes that start with \"LAP\".\n\nWhich criterion should you use?", "options": ["*LAP", "LAP*", "?LAP", "*LAP*"], "answer": 1},
  {"q": "A dataset contains employee salaries, but some salary cells are blank. You need to sort salaries from highest to lowest while keeping the dataset intact.\n\nWhat should you expect?", "options": ["Blank cells become the highest values", "Blank values are generally placed toward the bottom when sorting descending", "Rows containing blanks are automatically deleted", "Excel fills blanks with zero"], "answer": 1},
  {"q": "You are working with 8,000 rows and want the header row to remain visible while scrolling down.\n\nWhich feature should you use?", "options": ["Split", "Freeze Panes", "Page Break", "View Side by Side"], "answer": 1},
  {"q": "Cell A2 contains:\n    BLR-10458\n\nWhich formula extracts the first three characters?", "options": ["=LEFT(A2,3)", "=RIGHT(A2,3)", "=MID(A2,3)", "=LEN(A2,3)"], "answer": 0},
  {"q": "You have:\n    First Name in A2 = Riya\n    Last Name in B2 = Sharma\n\nWhich formula combines them with a space between them?", "options": ["=CONCAT(A2,B2)", "=CONCAT(A2,\" \",B2)", "=COMBINE(A2,B2)", "=JOIN(A2+B2)"], "answer": 1},
  {"q": "You filter a sales dataset to show only Bengaluru records.\n\nWhich function is particularly useful for calculating a total that changes based on filtered rows?", "options": ["SUM", "SUBTOTAL", "COUNTIF", "SUMPRODUCT"], "answer": 1},
  {"q": "A VLOOKUP formula returns #N/A even though the value appears visually identical in both tables.\n\nWhich is the most likely data issue to investigate first?", "options": ["Different font sizes", "Extra spaces or inconsistent text formatting", "Different column widths", "Hidden gridlines"], "answer": 1},
  {"q": "You need the third-highest sales value from a list.\n\nWhich function is most directly suitable?", "options": ["LARGE", "MAX", "RANK.EQ", "HIGH"], "answer": 0},
  {"q": "Column A contains 10,000 customer transactions but some customers appear multiple times.\n\nWhat is the best modern Excel approach to obtain the number of unique customers?", "options": ["COUNT(A:A)", "COUNTA(A:A)", "COUNTA(UNIQUE(A2:A10001))", "SUM(A:A)"], "answer": 2},
  {"q": "You want to show how total revenue is distributed among four business divisions.\n\nWhich chart could be appropriate?", "options": ["Pie/Donut chart", "Line chart", "Scatter plot", "Histogram only"], "answer": 0},
  {"q": "In =INDEX(A1:D10,3,2), what does the value 3 represent?", "options": ["Column number", "Row number", "Table number", "Match type"], "answer": 1},
  {"q": "In SUMIFS, which argument comes first?", "options": ["The first criteria range", "The criteria", "The sum range", "The sheet name"], "answer": 2},
  {"q": "A VLOOKUP fails to match values that look identical. What is the most likely cause?", "options": ["Different cell colors", "Hidden columns", "Trailing/leading spaces or inconsistent formatting", "Different font sizes"], "answer": 2},
  {"q": "Which chart type is most appropriate for showing a trend in monthly revenue over two years?", "options": ["Pie chart", "Line chart", "Donut chart", "Scatter plot"], "answer": 1},
  {"q": "A correlation coefficient of -0.85 between price and demand indicates:", "options": ["A strong positive relationship", "A weak relationship", "A strong negative relationship", "No relationship"], "answer": 2},
  {"q": "Which statistical method is commonly used to detect outliers in a dataset?", "options": ["Interquartile Range (IQR)", "VLOOKUP", "SUMIFS", "Data Validation"], "answer": 0},
  {"q": "Which function is designed to catch and manage formula errors such as #DIV/0!?", "options": ["=ERROR()", "=ISERROR()", "=IFERROR()", "=CHECKERR()"], "answer": 2},
  {"q": "What is the primary purpose of Power Query in Excel?", "options": ["To create charts automatically", "To import, clean, and transform data before loading it into a worksheet", "To protect a workbook with a password", "To record keyboard shortcuts"], "answer": 1},
  {"q": "A2:A10 contains Employee IDs and D2:D10 contains salaries. Which combination returns the salary for the ID in F2?", "options": ["=INDEX(A2:A10,MATCH(F2,D2:D10,0))", "=INDEX(D2:D10,MATCH(F2,A2:A10,0))", "=MATCH(D2:D10,F2,0)", "=XLOOKUP(D2:D10,F2,A2:A10)"], "answer": 1},
  {"q": "Which combination can dynamically return a sorted list of unique customers?", "options": ["=SUM(UNIQUE())", "=SORT(UNIQUE(A2:A100))", "=FILTER(SUM(A2:A100))", "=MATCH(SORT(A2:A100))"], "answer": 1},
  {"q": "A dashboard KPI shows Total Sales, but users want to interactively change the Region. Which control would be most suitable?", "options": ["Text Box", "Shape", "Slicer connected to the underlying PivotTable", "Page Break"], "answer": 2},
  {"q": "What does Power BI primarily allow users to do?", "options": ["Write and compile C++ programs", "Connect to, transform, model, and visualize data for business intelligence", "Manage email servers", "Design mobile app UIs only"], "answer": 1},
  {"q": "Which of these is a valid SQL aggregate function?", "options": ["COUNT()", "LENGTH_OF()", "TOTALX()", "GROUPX()"], "answer": 0},
  {"q": "Which command is used to remove a table entirely, including its structure, from a database?", "options": ["DELETE TABLE", "REMOVE TABLE", "DROP TABLE", "TRUNCATE COLUMN"], "answer": 2},
  {"q": "What does the SQL keyword DISTINCT do?", "options": ["Sorts results alphabetically", "Removes duplicate rows from the result set", "Locks a table for editing", "Creates an index on a column"], "answer": 1},
  {"q": "What is the purpose of the SQL WHERE clause?", "options": ["To sort results", "To filter rows based on a specified condition", "To create a new table", "To group rows together"], "answer": 1},
  {"q": "Which statement correctly creates a new table named 'Customers' with a single column 'CustomerID' of integer type?", "options": ["NEW TABLE Customers (CustomerID INT)", "CREATE TABLE Customers (CustomerID INT)", "MAKE TABLE Customers (CustomerID INT)", "TABLE CREATE Customers (CustomerID INT)"], "answer": 1}
];

const PROPS = PropertiesService.getScriptProperties();
const RUN_BUDGET_MS = 4.5 * 60 * 1000;   // leave headroom under Google's 6-minute limit
const START = Date.now();

function createQuizForm() {
  clearContinuation_();

  const existingId = PROPS.getProperty('FORM_ID');
  if (existingId) {
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
  PROPS.setProperty('FORM_ID', form.getId());
  if (CONFIG.CLOSE_AT) scheduleClose_(new Date(CONFIG.CLOSE_AT));
  logLinks_(form);
  emailLinks_(form);
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
    item.setTitle('Answer for Question ' + (i + 1))
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
