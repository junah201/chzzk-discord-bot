import MarkdownView from 'react-showdown';
import sanitizeHtml from 'sanitize-html';

interface MarkdownProps {
  text: string;
  options?: any;
  allowedTags?: string[];
  components?: any;
}

export const Markdown = ({
  text,
  options = {},
  allowedTags = [],
  components = {},
}: MarkdownProps) => {
  return (
    <div
      className="markdown-body w-full"
      style={{
        maxWidth: '920px',
        wordBreak: 'keep-all',
      }}
    >
      <MarkdownView
        markdown={text}
        options={{
          openLinksInNewWindow: true,
          underline: true,
          omitExtraWLInCodeBlocks: true,
          // literalMidWordUnderscores: true,
          simplifiedAutoLink: true,
          tables: true,
          strikethrough: true,
          smoothLivePreview: true,
          tasklists: true,
          ghCompatibleHeaderId: true,
          encodeEmails: true,
          ...options,
        }}
        components={components}
        sanitizeHtml={(html) =>
          sanitizeHtml(html, {
            allowedTags: [
              'addr',
              'address',
              'article',
              'aside',
              'h1',
              'h2',
              'h3',
              'h4',
              'h5',
              'h6',
              'section',
              'blockquote',
              'dd',
              'div',
              'dl',
              'dt',
              'hr',
              'li',
              'ol',
              'p',
              'pre',
              'ul',
              'a',
              'abbr',
              'b',
              'bdi',
              'bdo',
              'br',
              'cite',
              'code',
              'data',
              'dfn',
              'em',
              'i',
              'kbd',
              'mark',
              'q',
              'rb',
              'rp',
              'rt',
              'rtc',
              'ruby',
              's',
              'samp',
              'small',
              'span',
              'strong',
              'sub',
              'sup',
              'time',
              'u',
              'var',
              'wbr',
              'caption',
              'col',
              'colgroup',
              'table',
              'tbody',
              'td',
              'tfoot',
              'th',
              'thead',
              'tr',
              'del',
              'ins',
              'img',
              'svg',
              'path',
              'input',
              ...allowedTags,
            ],
            allowedAttributes: false,
            allowedClasses: {
              '*': ['align-middle'],
              a: ['anchor', 'mr-1'],
              svg: ['octicon-link'],
              img: ['emoji', 'special'],
            },
            allowedStyles: {},
          })
        }
      />
    </div>
  );
};

export default Markdown;
