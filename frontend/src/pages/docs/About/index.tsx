import { Box } from '@mui/material';
import { useState, useEffect } from 'react';

import Copyright from '@/components/Copyright';
import { Markdown } from '@/components/Markdown';
import PageButton from '@/components/PageButton';
import { getDocsMarkdown } from '@/lib/Github';

export const About = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    getDocsMarkdown('junah201', 'chzzk-discord-bot', 'docs/about.md').then(
      (data) => {
        setMarkdown(data);
      }
    );
  }, []);

  return (
    <Box>
      {markdown === '' ? (
        <></>
      ) : (
        <>
          <Markdown text={markdown} />
          <PageButton
            nextPath="/docs/getting-started"
            nextText="알림 등록하기"
          />
          <Copyright />
        </>
      )}
    </Box>
  );
};

export default About;
