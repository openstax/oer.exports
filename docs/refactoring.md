# Stylesheet Refactoring

# Goals

The main goals of re-factoring the book stylesheets are as follows:

- Separate style rules from selectors. This will allow an easy transition to different DOM structures (Eg, Moving from Docbook to XHTML).
- To be able to style books by supplying alternate ?slots? -- style rules for specific logical pieces of a book (An exercise, a section in a chapter, a solution in an exercise, a figure in a feature, etc.)

# Design

The primary design goal of this refactor is to split the stylesheets into layers which define two parts:

## Slots

A Slot is a piece of stylesheet which defines the style of a logical piece of a book (An exercise, a section in a chapter, a solution in an exercise, a figure in a feature, etc.). The most immediately beneficial result of this refactor is that styling new books should only require a minimum of effort ? that required to import base slots/skeletons and to supply only those alternative slots which are necessary to meet the design goals of the new book. The highest level book less files (eg, psychology.less) should only contain imports, variable declarations (colors, string constants, etc), and slots. 

## Skeletons

A Skeleton is a piece of stylesheet which ties slots to the DOM. These define the selectors to which slots are applied, and call any less mixins necessary to generate the final css output. Where possible skeleton files should not contain style rules.

# Slots

This section documents the slots which provide styling rules for the various logical structures of a book. Slots are provided via namespaced mixins (http://lesscss.org/#-namespaces). Outlined below is the structure of the average book, and the various slots provided to style each piece.


## Page

Provided via `page-slots.less`

### Numbering

    #page>#left,#right>.top-corner() { ... };

### Header

    #page>#left,
    #right>.top() { ... };
    
### "this content is available for free ...."

    #page>#left>.bottom() { ... };

### Title Page

T.B.D.

## Book-level Table of Contents

Provided via `ccap-base-slots.less`

### Title

    #toc>.title() { ... }; // The main ToC title.
    #toc>#entry>.title(unit);
    #toc>#entry>.title(chapter);
    #toc>#entry>.title(section); 

### Page

    #toc>#entry>.page() { ... }; // Chapter X : Y ?.... Z

## Parts

### Preface
### Chapter
### Appendix

## Content

Please see Slot Scope/Context before reading this section.

### Note

    #content>#note>.style() { ... };
    #content>#note>.title() { ... };
    #content>#note>.body() { ... };

### Footnote

    #content>#footnote>.style() { ... };

### Section

    #content>#section>#abstract>.style() { ... };
    #content>#section>#abstract>.list() { ... };
    #content>#section>#abstract>.list-item() { ... };

### Example

    #content>#example>.style() { ... };

### Exercise

    #content>#exercise>.style() { ... };

### Equation

    #content>#equation>.style() { ... };
    #content>#equation>.label() { ... };

### Figure

    #content>#figure>.style() { ... };

### Table

    #content>#table>.style() { ... };
    #content>#table>.header() { ... };
    #content>#table>.cell() { ... };
    #content>#table>.caption() { ... };

## Index

Provided via ccap-base-slots.less

    #index>.style() { ... };
    #index>.title() { ... };
    #index>.letter() { ... };
    #index>.term() { ... };
    #index>.link() { ... };

## Attribution

T.B.D.

# Slot Scope/Context

TODO.

# Developing Skeletons and Book Series

TODO.
