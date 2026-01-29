import { Box } from '@mui/material';
import { useState, useEffect } from 'react';

import Copyright from '@/components/Copyright';
import { Markdown } from '@/components/Markdown';
import PageButton from '@/components/PageButton';
import { getDocsMarkdown } from '@/lib/Github';

export const About = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    getDocsMarkdown('junah201', 'chzzk-discord-bot', 'docs/mention.md').then(
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
            prevPath="/docs/getting-started"
            prevText="알림 등록하기"
            nextPath="/docs/chzzk-id"
            nextText="Chzzk ID 사용법"
          />
          <Copyright />
        </>
      )}
    </Box>
  );
};

export default About;
