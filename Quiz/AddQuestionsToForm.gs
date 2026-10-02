/**
 * Adds questions 45-50 to the existing 44-question quiz form, so one form holds all 50,
 * and renames every answer heading to just "Answer".
 * Run addQuestionsToForm() once. Running it again is safe: nothing is added twice.
 */
const FORM_ID = '1ruTBdglr1HJZYT-32WB4PiVW9ThmQiMdyVFcNZU9mHU';
const FIRST_NUMBER = 45;
const IMAGE_FOLDER_NAME = 'Quiz Question Images';
const ANSWER_TITLE = 'Answer';

const NEW_QUESTIONS = [
  {"q": "In Power BI, which function is most appropriate when you want to calculate total sales only for the current filter context, while modifying one specific filter?", "options": ["SUM()", "CALCULATE()", "FILTER()", "SUMX()"], "answer": 1},
  {"q": "You have a Sales table and a Product table. The Product table contains Product ID as a unique value, while the Sales table contains multiple records for each Product ID.\n\nWhat relationship should generally be created?", "options": ["One-to-one", "Many-to-many", "One-to-many, with Product on the \"one\" side", "Many-to-one, with Product on the \"many\" side"], "answer": 2},
  {"q": "You create a measure:\n    Total Sales = SUM(Sales[Amount])\nYou place Year from a Date table on the X-axis of a visual.\n\nWhat happens to the Total Sales measure?", "options": ["It always shows the same total for every year", "It automatically calculates sales separately for each year based on filter context", "It produces an error because SUM() cannot work with dates", "It requires FILTER() to calculate yearly sales"], "answer": 1},
  {"q": "In an Excel regression output, the R² is 0.80 while the Adjusted R² is 0.74.\n\nWhich statement best explains the difference?", "options": ["The model explains 74% of the variation in the dependent variable.", "Adjusted R² accounts for the number of independent variables in the model and penalizes unnecessary variables.", "Adjusted R² is always higher than R².", "The difference means the regression model is statistically insignificant."], "answer": 1},
  {"q": "In an Excel regression output, an independent variable has a p-value of 0.03.\n\nAt a 5% significance level, what can you conclude?", "options": ["The variable is statistically significant", "The variable is statistically insignificant", "The R² is 0.03", "There is a 3% chance that the regression model is correct"], "answer": 0},
  {"q": "In Tableau, you have a sales dataset containing Region, Product, Sales, and Profit. You want to display Sales by Region and allow the user to select a specific Product using a dropdown.\n\nWhich Tableau feature would you primarily use?", "options": ["Calculated Field", "Filter", "Parameter", "Measure Names"], "answer": 1}
];

function addQuestionsToForm() {
  const form = FormApp.openById(FORM_ID);
  const titles = form.getItems().map(function (it) { return it.getTitle(); });
  if (titles.indexOf('Question ' + FIRST_NUMBER) === -1) {
    const images = drawImages_();
    NEW_QUESTIONS.forEach(function (q, k) {
      form.addImageItem()
        .setTitle('Question ' + (FIRST_NUMBER + k))
        .setImage(images[k])
        .setAlignment(FormApp.Alignment.CENTER)
        .setWidth(740);

      const item = form.addMultipleChoiceItem();    // single-select (radio buttons)
      item.setTitle(ANSWER_TITLE)
        .setChoices(q.options.map(function (opt, j) { return item.createChoice(opt, j === q.answer); }))
        .setPoints(1)
        .setRequired(false);                        // never block a timed auto-submit
    });
    Logger.log('Added questions ' + FIRST_NUMBER + '-' + (FIRST_NUMBER + NEW_QUESTIONS.length - 1) + '.');
  } else {
    Logger.log('Questions ' + FIRST_NUMBER + '+ are already in the form.');
  }

  let renamed = 0;
  form.getItems(FormApp.ItemType.MULTIPLE_CHOICE).forEach(function (it) {
    if (it.getTitle() !== ANSWER_TITLE) { it.setTitle(ANSWER_TITLE); renamed++; }
  });
  Logger.log('Renamed ' + renamed + ' answer headings to "' + ANSWER_TITLE + '".');
  logLinks_(form);
}

/** Draws each new question on a temporary Slides page and saves it as Qnn.jpg (reuses existing ones). */
function drawImages_() {
  const folders = DriveApp.getFoldersByName(IMAGE_FOLDER_NAME);
  const folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(IMAGE_FOLDER_NAME);
  const name = function (k) { return 'Q' + (FIRST_NUMBER + k) + '.jpg'; };

  const deck = SlidesApp.create('Quiz question images (temporary)');
  try {
    const blank = deck.getSlides()[0];
    const pageIds = NEW_QUESTIONS.map(function (q, k) {
      const slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
      slide.getBackground().setSolidFill('#FFFFFF');
      slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, 8, 405).getFill().setSolidFill('#1A7F37');
      slide.insertTextBox('Question ' + (FIRST_NUMBER + k), 40, 24, 640, 44).getText().getTextStyle()
        .setFontFamily('Roboto').setFontSize(26).setBold(true).setForegroundColor('#1A7F37');
      const size = q.q.length <= 120 ? 22 : q.q.length <= 220 ? 19 : 17;
      const body = slide.insertTextBox(q.q, 40, 80, 640, 300).getText();
      body.getTextStyle().setFontFamily('Roboto').setFontSize(size).setForegroundColor('#1F2328');
      body.getParagraphs().forEach(function (p) {
        const r = p.getRange();
        if (/^ {4}/.test(r.asString())) r.getTextStyle().setFontFamily('Roboto Mono').setBold(true);
      });
      return slide.getObjectId();
    });
    blank.remove();
    deck.saveAndClose();

    const token = ScriptApp.getOAuthToken();
    return pageIds.map(function (pageId, k) {
      const existing = folder.getFilesByName(name(k));
      if (existing.hasNext()) return existing.next().getBlob();
      const url = 'https://docs.google.com/presentation/d/' + deck.getId() + '/export/png?pageid=' + pageId;
      const jpg = fetchWithRetry_(url, token).getAs('image/jpeg').setName(name(k));
      folder.createFile(jpg);
      Utilities.sleep(2000);                        // stay under Google's export rate limit
      return jpg;
    });
  } finally {
    DriveApp.getFileById(deck.getId()).setTrashed(true);
  }
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
  throw new Error('Google is still rate-limiting image export. Wait a few minutes and run again.');
}

function logLinks_(form) {
  Logger.log('Edit link:    ' + form.getEditUrl());
  Logger.log('Student link: ' + form.getPublishedUrl());
}
