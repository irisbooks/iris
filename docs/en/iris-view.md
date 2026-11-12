# Your books on this computer (iris view)

`iris view` opens your books in the web app's screens, read straight from the
book files on your computer. You can read reports and journals, post drafts,
fix a draft, start a new entry or correct a posted one. It needs no account or
network and uploads nothing. Changes are ordinary edits to your files, and a
linked book carries them to the cloud at your next sync.

## Open it

```bash
iris view                           # the book you're in
iris view ~/IrisBooks/shop-2026     # one book
iris view --books-dir ~/IrisBooks   # every book in this folder
```

Run inside a book folder, `iris view` opens that book. With `--books-dir`, it
opens every book directly inside the folder and adds **Dashboard** and **Net
Worth** across them. Outside any book, it opens the last folder you used, or
asks which one.

The page opens in a window of its own, using Chrome or Edge with no address
bar and no extensions. Without either browser it opens in your default
browser; `--tab` asks for that on purpose. On a Mac, the window appears as
Google Chrome or Microsoft Edge in the Dock and the app switcher.

`iris view` returns at once. The page keeps working until you close it. When a
book in the folder also syncs with the cloud, the top bar says **Local copy**:
the page shows your files, and changes reach the cloud copy at your next sync.

## The launcher

To open your books without a terminal or an AI, use the IrisBooks launcher.
The installer adds it on a first install on a desktop. To add it yourself, or
again after removing it:

```bash
iris view --add-launcher
```

| System | Where it appears |
| --- | --- |
| macOS | **IrisBooks** in `~/Applications`. Find it with Spotlight, or drag it to the Dock. |
| Windows | **IrisBooks** in the Start Menu. |
| Linux | **IrisBooks** in your desktop's app menu. |

The launcher opens the last folder you used, or asks which one. It holds no
folder of its own, so one launcher reaches every folder. To set the folder it
opens first, name it when you add the launcher:
`iris view --books-dir ~/IrisBooks --add-launcher`. Add `--tab` to have the
launcher use your default browser.

`iris view --remove-launcher` removes it, and so does `iris uninstall`. If you
move `iris` somewhere else, add the launcher again.

## Choosing a folder

A colored strip above the top bar names the folder you're in. Its menu holds:

- **Recent folders**, to switch to one you've opened before.
- **Choose a folder**, which opens your system's folder picker. Where there's
  no picker, type the path into **Folder path** and choose **Open**.
- **Color**: Green, Blue, Teal, Plum, Rust, Brown, Ochre or Charcoal.

Choose a book's own folder, or a folder that holds several books. iris works
out which it is. Switching opens the other folder in the same window.

The color is there so you can tell folders apart at a glance, for example one
client's books from another's. A folder of books keeps its color in its own
`.irisbooks/settings.yaml`, so it looks the same wherever that folder is opened.
A single book's color is kept on this computer, because the book's own files
sync. A folder you haven't colored gets a color from its path, so different
folders usually look different from the start. To give every folder the same
starting color, set `color` in `~/.config/irisbooks/settings.yaml`; see
[prices and settings for a folder of books](cli-reference.md#prices-and-settings-for-a-folder-of-books).

Language and appearance are kept per folder. The book's language applies the
first time; after that, the language switch in the top bar decides.

## What you can see

These screens work as they do in [the web app](web-app.md), with figures
calculated by `iris` from your files:

- **Overview**, **Journals** and each entry's detail.
- The five reports: **General Ledger**, **Trial Balance**, **Profit & Loss**,
  **Balance Sheet** and **Monthly Trend**.
- **Chart of Accounts**, **Raw documents** and **Notes**.
- **Plugins**, which only this page has (see below).
- **Dashboard** and **Net Worth** across books, when the folder holds more than
  one. They include every book in the folder.

When you or your AI change a file, the page updates within a few seconds. There
is no **Run aggregation** step. As everywhere, reports count posted entries
only.

Screens that need the cloud copy aren't here: **Activity**, deleted journals,
**Year-end**, book settings, an entry's **History**, and adding a book. Use the
web app for those.

## Posting drafts

Open a draft, read it, and choose **Post**. To post several, select them in
**Journals**, choose **Review selected journals**, read each one, then choose
**Approve reviewed sources**. You can review up to 32 at a time.

Posting changes only `status: draft` to `status: posted`, the same as
`iris post --local`, and never syncs. On a linked book the page says "Posted on
this computer. It reaches the cloud at your next sync."

A post is refused, and the file left as it was, when:

- the entry changed after you opened it. Read it again, then post.
- a sync is running. Try again when it finishes.
- the book is set to post in the web app (**Posting approval** is on).
- the entry's fiscal year is closed. Reopen it first.
- the book is an archive.

The posting approval setting and closed years come from the book's last sync.

## Editing entries

On a draft's or a posted entry's page, choose **Edit**. Work on the **Form** or on the **Source**,
the file itself; you can switch between them. The form changes only what you
change, and keeps everything it doesn't show, such as comments, quantities and
fields from the book's overlays. An entry with accounting views opens as source
only.

- **As you type, the book's overlays calculate** what they can, the same as
  [`iris journal complete`](cli-reference.md#iris-journal-complete). A
  calculated amount appears in its blank field with a dashed outline, and a
  line an overlay would add appears below the others. Choose
  **Fill in** to enter them all at once; it also removes any row you added and
  left empty. **How it's calculated** works each calculated figure through from
  the figures it came from. An amount an overlay sets itself is
  explained by the reason the overlay gives, or by its own description, which
  follows. When two of the book's overlays calculate the entry differently,
  both results appear side by side; choose one, and it stays your choice while
  you keep editing. When the entry can't be calculated, the reason
  appears under the totals. Nothing is saved until you check the amounts and
  choose **Save**. An entry saved with a blank amount, draft or posted, still
  opens here so you can fill it in.
- **Save** writes the entry to `journals/YYYY-MM/`. Changing its date moves it
  to that month's folder.
- After each save, **Checks on the saved entry** runs the same checks as
  `iris validate`. It lists this entry's problems and counts errors elsewhere in
  the book.

Save refuses an entry that would stop the book's reports: a blank amount, a line
with no account or with both a debit and a credit, or a date outside the book's
fiscal year. It also refuses a change of status, because posting is a separate
step. An entry that names an account the chart doesn't have is saved and
flagged in the checks, and so is a draft that doesn't balance. **Post** stays
unavailable until the draft balances.

If the checks say the book's own overlay layer isn't trusted on this computer,
review it and run `iris overlay trust`.

A posted entry is changed in place and stays posted. Save refuses a change that
posting would refuse, so a posted entry always balances. On a linked book, the
cloud keeps the earlier version in the entry's history after your next sync; a
book that doesn't sync keeps no earlier version. You can't edit a posted entry
here when its fiscal year is closed, or when **Posting approval** is on, because
the server would refuse the change. To leave the posted entry as it was and
record the fix as a new entry, use **Correct this entry** instead.

## New entries and corrections

**New entry** on **Journals** starts a draft dated today. In a book for an
earlier year, it starts inside that year. The file is named from the date and
payee.

**Correct this entry**, on a posted entry, starts a new draft whose lines
reverse it, keeping its attachments. Add the right lines below them and save,
then post the correction. The posted entry stays exactly as it was.

## Plugins

**Plugins** lists the plugins this book keeps a copy of (`iris` calls them
[overlays](concepts.md#region-rules-the-overlay)), grouped as common or by
region, above the **Core checks** that always run. A plugin that needs another
is shown under it. Choose one to see what it adds to the book: checks,
calculations, suggested values, completions, fields, tasks and guides, and the
plugin's own notes.

To turn a plugin on or off, use its switch or **Turn on** / **Turn off**. The
page first shows what would change: the plugins that go with it (a plugin
that another one needs can't be turned off alone), what starts or stops, and
how many recorded results came from these plugins. Nothing is written until
you confirm, and then exactly what you reviewed; if the book changed in
between, you're asked to review again. The page changes `overlays:` in
`config/book.yaml`, as [`iris overlay select`](cli-reference.md#iris-overlay)
does. A plugin you turn off keeps its copy in the book, and figures recorded
with it are still checked. On a linked book the change reaches the cloud at
your next sync.

A plugin with **Settings** shows them in a form: the book-level fields it
declares, such as a choice between methods. A field appears when it applies,
so choosing one value can bring up others it needs. A setting that names
accounts or units offers the book's chart of accounts or its declared units, and
marks one the book doesn't have. A plugin that doesn't describe its settings
field by field is edited as YAML. Before you save, the
page shows the change to `config/book.yaml`, and it saves exactly that;
comments and other settings stay as they were. If the book changed in
between, you're asked to review again.

Nothing here can change while the book's fiscal year is closed or the book is
an archive.

**Available to add** lists the plugins that come with your version of `iris`
and that the book doesn't have yet; nothing is downloaded. **Add** shows the
same kind of review, plus the result of each plugin's own tests, then copies
the exact plugin into the book and turns it on, together with any plugin it
needs. A plugin for another region's books is listed under **Other regions**
and can't be added. Plugins released after your version of `iris` aren't
listed: ask your assistant, or run `iris overlay install --pin` with the exact
version. A newer version of a plugin the book already has is an upgrade: use
`iris overlay upgrade`.

The book's own definitions in `config/overlays/` appear at the top; they run
only after you trust them with `iris overlay trust`.

In [the demo](https://irisbooks.io/demo/) you can see what turning a plugin on
or off, adding one, or changing its settings would do, without changing
anything.

## Prices and currencies

**Net Worth** values your holdings with the prices recorded on this computer,
and with the folder's own prices if it has them. **Settings** lists them. To
record a price or exchange rate, ask your assistant or run
[`iris price add`](cli-reference.md#iris-price); add `--books-dir` to record it
for the folder.

A folder whose books use different currencies needs a reporting currency for the
Dashboard and Net Worth. Set `reporting_currency` in the folder's
`.irisbooks/settings.yaml` or in your `~/.config/irisbooks/settings.yaml`, or
pass `--currency`, for example
`iris view --books-dir ~/IrisBooks --currency JPY`. Each book still opens
without one. As in the web app, the Dashboard's rate boxes change that view
only and save nothing.

## Several windows

You can open several windows, on different folders or on the same one. Each
window shows the book named in that window's own address (URL).

If two windows change the same entry, the second save is refused with "This
entry changed after you opened it" and your text stays in the box. Copy what you
need, then choose **Reload the entry** to see the other window's change.

## Updates

**Settings → About** shows which version of `iris` is running. Choose **Check
for updates** to ask irisbooks.io for the latest version. If a newer one is out,
choose **Update to …**: `iris` downloads it, checks its signature and checksum,
replaces itself, and restarts the page, which reloads on its own. If the check
fails, the version you have stays in place.

Tick **Check automatically** to have the page ask at most once a day while it's
open. An **Update available** label then appears at the top of the page when
there's a newer version. Nothing installs until you choose **Update**. The
setting is yours on this computer, so it covers every folder you open.

If your AI app runs IrisBooks for you, restart that app after updating so it
uses the new version too. A copy installed as an extension in your AI app is
updated from that app's extension settings; the About section links to the
download. A development build can't update itself.

## Privacy and stopping

- The page is served by `iris` at `127.0.0.1` on this computer. It reads only
  the book files and needs no account. It sends nothing anywhere, except the
  version check described in [Updates](#updates) when you ask for it.
- `iris view` signs your browser in with a one-time link that it never prints.
- The window uses a browser profile of its own with extensions turned off, so a
  browser extension can't read your books through it. A tab in your everyday
  browser doesn't have that protection.

The page stops by itself about five minutes after you close the last window.
`iris view --stop` stops it now, and `iris view --status` says whether it's
running. A page left open after that says "This view has closed. Open IrisBooks
again."

Next: [Using the web app](web-app.md).
