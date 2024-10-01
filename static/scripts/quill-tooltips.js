var quillTooltips = {
    'header': {
        '1': 'Heading 1',
        '2': 'Heading 2',
        '3': 'Heading 3',
        'false': 'Normal Text'
    },
    'bold': 'Bold',
    'italic': 'Italic',
    'underline': 'Underline',
    'strike': 'Strikethrough',
    'blockquote': 'Blockquote',
    'code-block': 'Code Block',
    'list': {
        'ordered': 'Numbered List',
        'bullet': 'Bulleted List'
    },
    'script': {
        'sub': 'Subscript',
        'super': 'Superscript'
    },
    'indent': {
        '+1': 'Increase Indent',
        '-1': 'Decrease Indent'
    },
    'direction': 'Text Direction',
    'size': {
        'small': 'Small',
        'large': 'Large',
        'huge': 'Huge'
    },
    'align': {
        '': 'Align Left',
        'center': 'Align Center',
        'right': 'Align Right',
        'justify': 'Justify'
    },
    'link': 'Insert Link',
    'image': 'Insert Image',
    'clean': 'Clear Formatting'
};

function applyQuillTooltips() {
    $('.ql-toolbar button, .ql-toolbar .ql-picker').each(function() {
        var format = $(this).attr('class').split(/\s+/).find(cls => cls.startsWith('ql-')).slice(3);
        var value = $(this).attr('value') || '';

        if (format === 'list') {
            $(this).attr('title', quillTooltips[format][value] || 'List');
        } else if (quillTooltips[format]) {
            if (typeof quillTooltips[format] === 'object') {
                $(this).attr('title', quillTooltips[format][value] || format);
            } else {
                $(this).attr('title', quillTooltips[format]);
            }
        } else {
            $(this).attr('title', format);
        }
    });
}