# markdown.rpy contains Markdown configuration for Mistune that is used by
# Say Something submod in order to render Markdown to Ren'Py style tags.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init -80 python in _fom_saysomething_markdown:

    import mistune

    ## Plugins

    def spoiler(md):
        # This is a copy-paste from the source code, except it doesn't
        # add a block spoiler parser function here. And also modifies
        # the inline pattern a little (so it's Discord-like, ||spoiler||)
        INLINE_SPOILER_PATTERN = r'\|\|\s*(?P<spoiler_text>.+?)\s*\|\|'
        from mistune.plugins.spoiler import parse_inline_spoiler, render_inline_spoiler
        md.inline.register('inline_spoiler', INLINE_SPOILER_PATTERN, parse_inline_spoiler)
        if md.renderer and md.renderer.NAME == 'html':
            md.renderer.register('inline_spoiler', render_inline_spoiler)

    def underline(md):
        ## Underline parsing function
        def parse_inline_underline(inline, m, state):
            text = m.group('underline_text')
            new_state = state.copy()
            new_state.src = text
            children = inline.render(new_state)
            state.append_token({'type': 'underline', 'children': children})
            return m.end()

        ## Registering it
        INLINE_UNDERLINE_PATTERN = r'__\s*(?P<underline_text>.+?)\s*__'
        md.inline.SPECIFICATION["emphasis"] = r'\*{1,3}(?=[^\s*])|\b(_{1}|_{3})(?=[^\s_])'
        md.inline = mistune.inline_parser.InlineParser()
        md.inline.register('underline', INLINE_UNDERLINE_PATTERN, parse_inline_underline)

        # Not the best idea of Mistune developers to implement it GLOBALLY,
        # but hopefully no one else uses Mistune but us - otherwise we'd have
        # a collision point here, as we change GLOBAL dictionary here. Boo.
        if '__' in mistune.inline_parser.EMPHASIS_END_RE:
            del mistune.inline_parser.EMPHASIS_END_RE['__']

    def subset(md):
        # Disable unnecessary syntax
        md.block.rules.remove('fenced_code')
        md.block.rules.remove('indent_code')
        md.block.rules.remove('thematic_break')
        md.block.rules.remove('block_quote')
        md.block.rules.remove('list')
        md.block.rules.remove('ref_link')
        md.block.rules.remove('raw_html')

        # Actually, heading idea *isn't that bad*, but we sure need some logic
        # in place to make the TERRIBLY LARGE lines fit inside the dialog box.
        # While we don't it's better to leave this removed.
        md.block.rules.remove('axt_heading')
        md.block.rules.remove('setex_heading')

        # Disable inline syntax as well
        md.inline.rules.remove('codespan')
        md.inline.rules.remove('link')
        md.inline.rules.remove('auto_link')
        md.inline.rules.remove('auto_email')
        md.inline.rules.remove('inline_html')

    ## Renderer

    class RenPyRenderer(mistune.HTMLRenderer):
        def __init__(self):
            super(RenPyRenderer, self).__init__()

        ## Formatting

        def text(self, text): # Plain text
            return text.replace("{", "{{").replace("[", "[[")

        def emphasis(self, text): # *Emphasis*
            return '{i}' + text + '{/i}'

        def strong(self, text): # **Strong**
            return '{b}' + text + '{/b}'

        def strikethrough(self, text): # ~~Strikethrough~~
            return "{s}" + text + "{/s}"

        def inline_spoiler(self, text): # ||Spoiler||
            return "{=edited}" + text + "{=normal}"

        def underline(self, text): # __underline__
            return "{u}" + text + "{/u}"

        ## HTML overrides

        def linebreak(self):
            return '\n'

        def softbreak(self):
            return '\n'

        def paragraph(self, text):
            return text

        def blank_line(self):
            return '\n\n'

        def block_text(self, text):
            return text


    ## Markdown render function

    render = mistune.create_markdown(plugins=[underline, 'strikethrough', spoiler, subset],
                                     renderer=RenPyRenderer())