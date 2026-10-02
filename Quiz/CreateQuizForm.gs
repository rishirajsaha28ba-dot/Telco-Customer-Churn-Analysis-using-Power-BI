/**
 * Builds the Google Form quiz: one question image (JPEG) + one single-select MCQ per question.
 *
 * Just run createQuizForm() and approve permissions. The edit + student links are printed in the log.
 * If Q01.jpg ... Q44.jpg are already in your Drive they are used; otherwise the script draws
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
