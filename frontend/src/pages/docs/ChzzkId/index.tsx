import { Box } from '@mui/material';
import { useState, useEffect } from 'react';

import Copyright from '@/components/Copyright';
import { Markdown } from '@/components/Markdown';
import PageButton from '@/components/PageButton';
import { getDocsMarkdown } from '@/lib/Github';

export const ChzzkId = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    getDocsMarkdown('junah201', 'chzzk-discord-bot', 'docs/chzzk_id.md').then(
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
          <PageButton prevPath="/docs/mention" prevText="멘션 사용법" />
          <Copyright />
        </>
      )}
    </Box>
  );
};

export default ChzzkId;
