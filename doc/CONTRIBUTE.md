# Development Guidelines

## Important Donts

* NEVER EVER READ SHELL ENV VARIABLES
* Don't commit code without ruff linting checks
* Never implement without associated test
* Delete parts of `deleteme-normpic-modules/` as they become obsolete
* Consider `deleteme-normpic-modules/` when specs arise around ordering or timestamp precedence

## Testing Requirements

* This is a `**uv**`` managed project
  * **Test Command**: Use `uv run pytest` to run tests
    * **NOT**: `python -m pytest`
* **Specific Test Files**:
  * Use `uv run pytest test/test_filename.py -v` for focused testing
  * **ALWAYS** run full suites before every commit
* Follow E2E + TDD approach:
  * E2E/Integration tests to surface larger missing or broken pieces
    * Therefore they should be prioritized first
    * Nest into Unit tests when missing or broken piece discovered
      * Should try and find existing tests needing modification first.
      * If no test exists for that spec, make a new one
  * TDD fills or fixes those pieces incrementally
  * Build tests singularly first
  * Ensure test fails as expected (red)
  * Implement change to make test pass (green)
  * Consider refactors for better solution (refactor)
  * Move to next test when complete or to parent integration/E2E test
* Task management:
  * Each test typically corresponds to a TODO task
  * Some tasks require multiple tests
  * After test(s) pass and refactors complete: update TODO.md, update documentation, git commit
* Pre-commit documentation process:
  * Mark completed TODO items as done
  * Add entry to doc/CHANGELOG.md with H2 date header and bullet points
  * Document architectural decisions in doc/architecture/ or doc/modules/
  * Delete completed TODO entries to prevent size explosion
  * TODO should shrink overall as MVP approaches completion
* Documentation updates (Green phase):
  * When tests pass, update relevant documentation in `doc/`
  * Each subdirectory in `doc/` represents a topic
  * Follow documentation hierarchy: documents link to same-level README → subdirectory README → parent README
  * Only top-level README provides high-level overviews and links to directory-level or subdirectory READMEs
  * **CRITICAL**: Every document must be linked in the documentation hierarchy starting from doc/README.md
  * No document should be a link orphan - all must be discoverable through the hierarchy
* Implement in small steps with clear logical breaks:
  * Add one test case or feature at a time
  * Test immediately after each testable addition
  * Never write massive amounts of code without testing

## Commit Message Format

* Title: Maximum 50 characters including prefix
* Body: Maximum 72 characters per line
* Body text should use '-' bullets with proper nesting
* Use prefixes:
  * `Tst:` for test-related changes
  * `Fix:` for bug fixes
  * `Ft:` for new features
  * `Ref:` for refactoring
  * `Doc:` for documentation
  * `Pln:` for planning/TODO updates
* No signature block - do not include emoji, links, or Co-Authored-By lines

## Code Style

* Follow existing patterns in the codebase
* Check neighboring files for conventions
* Never assume a library is available - verify in package.json/requirements
* Functions should have a proper docstring
* We type annotate our code and prefer dataclasses for basic data structures
* Match indentation and formatting of existing code
* Follow PEP 8, ruff and typical Python conventions:
  * No trailing whitespace
  * Blank line at end of file
  * Two blank lines between top-level definitions
  * One blank line between method definitions
  * Spaces around operators and after commas
  * No unnecessary blank lines within functions
  * Maximum line length of 88 characters (Black/Ruff default)
* **2-space indentation** throughout templates and JS
  * **NOT** Python - Python uses 4 spaces

## Key Implementation Details

* **Local-only MVP**:
  * Rename files to proper time & photographer order & counter filenames
  * Source of time truth occurs in this order:
    * EXIF timestamp
      * Subsecond if it has it
        * otherwise from same src filenames with same/adjacent timestamps
      * Any other ordering EXIF data
    * Filename sequencing order
    * FS timestamps
  * Ordering conflicts
    * Filename lexically orders to this order
    * Timestamp goes first
    * Need an ability to handle same/similar timestamps by different cameras
    * Then choose a camera by EXIF make/model
      * Bursts shouldn't be interrupted by another camera
        * even if next timestamp+subsec by other camera suggests it's next
    * Final filename:
      * `collection_name`
        * The name of the collection
        * *i.e. wedding, graduation, Crete holiday, etc.*
        * kebab case for everything
        * Could be blank, in which case don't include following '-' hyphen
      * `timestamp`
        * Format: `YY-MM-DDTHHMMSS` in 24hr local time
        * No `Z` or UTC offset characters like in the ISO standard
        * Assumed local timezone unless timezone specified
        * May implement Explicit UTC timezone offsets in future
      * `camera`
        * EXIF extracted camera make/model
        * Usually a string
        * I know for a fact the real world first collection this will use...
          * ...has a string `r5a` for its cameras (more than one of them)
        * Could be missing
          * in which case don't include nor its following `-` separator
      * `count`
        * Counter to order bursts with
        * Single Base32 (Hex) digit
        * 32 is enough burst ordering for a single timestamp
        * Very often, no need for a counter, so don't include it if not needed
          * This includes the separator `-` before it
      * Final filename format:
        * `{collection_name-?}{timestamp}{-camera?}{-count?}.{extension}`
  * Default is to simply symlink from source to destination for each pic
    * Only case it's impossible if config specifies something overriding EXIF
      * Not a case we will implement in MVP
  * Follows config JSON
  * Produces manifest.json in destination directory
    * Uses schema validated JSON for interoperability by other programs
    * Holds configs that produced it
    * Holds timestamp for its modification time
    * For each photo:
      * Timestamp of best-effort guess from available metadata for pic creation
        * The source of truth that gave the timestamp
      * Hash of source photo & destination photo
        * Image data shouldn't be modified
          * but EXIF could be, causing a different destination hash
      * Size of file
      * Camera make/model (if available)
      * GPS coords (if available)
      * Timeszone/UTC offset (if available)
  * In short:
    * users should be able to scroll through and clearly see the order of events
    * Only exception is bursts should be adjacent from same camera/photographer
    * And it should be possible with lexical sorting of filename

* **Post MVP (near term)**:
  * Implement configurable for symlink vs copy
  * S3-compatible is next adaptor/integration post-MVP
  * Rich CLI styling
    * Textual TUI (eventually)
  * UTC offset, implied by EXIF or GPS or explicitly through config
  * Timestamp systematic correction through config
  * SSH/SFTP
  * Proton Drive

## Project-Specific Instructions

* This is a photo collection management utility
* Ensures a original copy exists while maintaining a more frequently used copy
* Current focus areas are tracked in TODO.md
* Keep TODO.md updated:
  * Update "Current Tasks" section when starting/stopping work
  * Mark completed items with [x]
  * Add new tasks as they're discovered
  * Document progress for easy resumption
* Keep `./doc` updated
  * `doc/README.md`
    * The overview and index to other documentation documents
  * The rest are named after key documentation topics
  * If a new documentation topic is needed:
    * Check if a pre-existing document just needs updating or adding to
      * If not - check with topic directory it should be in
        * If a new one is needed - create a new topic directory/subdir
  * Ensure a chain of doc links leading from project root README to doc exists
* The only document every contribution should need is the root README.md
  * From there it should be clear what if any other documents need reading

## Important Reminders

* Do what has been asked; nothing more, nothing less
* NEVER create files unless they're absolutely necessary for achieving your goal
* ALWAYS prefer editing an existing file to creating a new one
