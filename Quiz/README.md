# Quiz: question JPEGs + Google Form (MCQ, single-select, timed)

| File | What it is |
|---|---|
| `images/Q01.jpg` … `images/Q44.jpg` | One JPEG per question with the question text only (no options) |
| `quiz_images.zip` | All 44 JPEGs in one zip for uploading to Google Drive |
| `CreateQuizForm.gs` | Google Apps Script that builds the Google Form |
| `questions.json` | Source of truth: question text, 4 options, correct answer index |
| `make_images.py`, `make_form_script.py` | Regenerate the JPEGs / the Apps Script after editing `questions.json` |

## Build the Google Form (about 3 minutes)

1. In Google Drive, make a new folder, unzip `quiz_images.zip`, and upload the 44 JPEGs into it.
   Copy the folder ID from the URL: `drive.google.com/drive/folders/<FOLDER_ID>`.
2. Open <https://script.google.com>, choose **New project**, delete the sample code and paste in the contents of `CreateQuizForm.gs`.
3. In `CONFIG`, set `DRIVE_FOLDER_ID` (and `TITLE` / `TIME_LIMIT_MINUTES` if you want to change them).
4. Select `createQuizForm` and click **Run**. Approve the permissions. The edit link and student link appear in **Execution log**.

The form you get:
- Each question appears as its JPEG, followed by a **single-select multiple-choice** item with options A–D.
- Quiz mode is on, the answer key is filled in (1 point each), so responses are graded automatically.
- Responses collect emails and are limited to one per user. Respondents must sign in to Google.

## Timer and auto-submit

Google Forms has **no built-in countdown or auto-submit**, and Apps Script cannot add one to the respondent's page. Use the free **Form Timer** add-on:

1. Open the form in edit mode, then go to **⋮ (More) → Add-ons**, search for **Form Timer**, and install it.
2. Open the add-on (puzzle icon → Form Timer), set the duration (e.g. 30 min), and switch on **auto-submit**.
3. Share the timer link the add-on gives you, **not** the normal form link. Each student's countdown starts when they open it, and the form submits itself when time runs out.

Questions are deliberately **not marked required**, so an auto-submit is never blocked by unanswered questions. When the timer auto-submits, whatever the student has answered so far is recorded, and unanswered questions score 0.

**Optional hard deadline:** set `CONFIG.CLOSE_AT` (e.g. `'2026-10-05T11:30:00'`) before running the script. A trigger then stops the form from accepting responses at that time for everyone. Closing the form does **not** save the answers of anyone still filling it in, so set `CLOSE_AT` a few minutes *after* the timer ends and let the timer's auto-submit save partial answers.

## Answer key
1-D 2-A 3-B 4-D 5-B 6-D 7-C 8-C 9-B 10-C 11-C 12-A 13-B 14-A 15-B 16-B 17-B 18-B 19-B 20-B 21-A 22-B
23-B 24-B 25-A 26-C 27-A 28-B 29-C 30-C 31-B 32-C 33-A 34-C 35-B 36-B 37-B 38-C 39-B 40-A 41-C 42-B 43-B 44-B

Q16–Q19 had no highlighted answer in the source PDF. The key above uses the standard correct answers for those questions; check them before you publish.
